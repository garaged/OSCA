use serde_json::Value;
use std::collections::HashMap;
use std::env;
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::os::fd::AsRawFd;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use tauri::Manager;

const MAX_MESSAGE_BYTES: usize = 1_048_576;
const SIDECAR_TIMEOUT: Duration = Duration::from_secs(15);
const SIDECAR_POLL_INTERVAL: Duration = Duration::from_millis(25);
const LOCK_EX: i32 = 2;
const LOCK_NB: i32 = 4;
const FNV_OFFSET_BASIS: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;
const BROKER_OWNED_PROFILE_ENV: &str = "OSCA_DESKTOP_OWNED_PROFILE";

unsafe extern "C" {
    fn flock(fd: i32, operation: i32) -> i32;
}

struct ProfileSessionLease {
    profile_root: String,
    _file: File,
}

#[derive(Default)]
struct BrokerState {
    leases: Mutex<HashMap<String, ProfileSessionLease>>,
}

impl BrokerState {
    fn opened_profile(&self, window_label: &str) -> Result<Option<String>, String> {
        let leases = self
            .leases
            .lock()
            .map_err(|_| "desktop profile-session state is unavailable".to_string())?;
        Ok(leases
            .get(window_label)
            .map(|lease| lease.profile_root.clone()))
    }

    fn owns_profile(&self, window_label: &str, profile_root: &str) -> Result<bool, String> {
        Ok(self.opened_profile(window_label)?.as_deref() == Some(profile_root))
    }

    fn require_owner(&self, window_label: &str, profile_root: &str) -> Result<(), String> {
        if self.owns_profile(window_label, profile_root)? {
            Ok(())
        } else {
            Err(
                "profile mutation requires this OSCA window to open and own the profile first"
                    .to_string(),
            )
        }
    }

    fn commit_lease(&self, window_label: &str, lease: ProfileSessionLease) -> Result<(), String> {
        let mut leases = self
            .leases
            .lock()
            .map_err(|_| "desktop profile-session state is unavailable".to_string())?;
        leases.insert(window_label.to_string(), lease);
        Ok(())
    }

    fn release_window(&self, window_label: &str) {
        if let Ok(mut leases) = self.leases.lock() {
            leases.remove(window_label);
        }
    }
}

#[tauri::command]
fn desktop_request(
    window: tauri::WebviewWindow,
    state: tauri::State<'_, BrokerState>,
    request_json: String,
) -> Result<String, String> {
    validate_request_size(&request_json)?;
    let (method, profile_root) = request_context(&request_json)?;
    let window_label = window.label().to_string();

    let mut pending_lease = None;
    let mut broker_owned_profile = None;
    if matches!(method.as_str(), "profile.open" | "profile.create") {
        let root = profile_root
            .as_deref()
            .ok_or_else(|| format!("{method} requires profile_root"))?;
        if !state.owns_profile(&window_label, root)? {
            pending_lease = Some(acquire_profile_session_lease(root)?);
        }
        broker_owned_profile = Some(root.to_string());
    } else if method == "profile.select" {
        // Selection is a preference only. A later successful select releases this window's
        // open-profile ownership without affecting any other window's session.
    } else if let Some(root) = profile_root.as_deref() {
        let owns_profile = state.owns_profile(&window_label, root)?;
        if is_profile_mutation(&method) {
            state.require_owner(&window_label, root)?;
        }
        if owns_profile {
            broker_owned_profile = Some(root.to_string());
        }
    }

    let bundled_sidecar = bundled_sidecar_path(window.app_handle());
    let decoded = invoke_sidecar(
        &request_json,
        broker_owned_profile.as_deref(),
        bundled_sidecar.as_deref(),
    )?;
    let succeeded = response_succeeded(&decoded)?;

    if succeeded {
        if let Some(lease) = pending_lease {
            state.commit_lease(&window_label, lease)?;
        }
        if method == "profile.select" {
            state.release_window(&window_label);
        }
    }

    let opened_profile = state.opened_profile(&window_label)?;
    override_window_profile(&decoded, &method, opened_profile.as_deref())
}

fn invoke_sidecar(
    request_json: &str,
    broker_owned_profile: Option<&str>,
    bundled_sidecar: Option<&str>,
) -> Result<String, String> {
    let (program, args) = sidecar_invocation(
        env::var("OSCA_DESKTOP_SIDECAR").ok(),
        env::var("OSCA_DESKTOP_PYTHON").ok(),
        bundled_sidecar.map(str::to_string),
    );
    let mut command = Command::new(program);
    command.args(args);
    apply_sidecar_profile_authorization(&mut command, broker_owned_profile);

    let mut child = command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|error| format!("unable to start OSCA sidecar: {error}"))?;

    let mut stdin = child
        .stdin
        .take()
        .ok_or_else(|| "sidecar stdin unavailable".to_string())?;
    stdin
        .write_all(format!("{request_json}\n").as_bytes())
        .map_err(|error| format!("unable to write sidecar request: {error}"))?;
    drop(stdin);

    let deadline = Instant::now() + SIDECAR_TIMEOUT;
    loop {
        match child.try_wait() {
            Ok(Some(_)) => break,
            Ok(None) if Instant::now() < deadline => thread::sleep(SIDECAR_POLL_INTERVAL),
            Ok(None) => {
                let _ = child.kill();
                let _ = child.wait();
                return Err("OSCA sidecar request timed out".to_string());
            }
            Err(error) => return Err(format!("unable to inspect OSCA sidecar status: {error}")),
        }
    }

    let output = child
        .wait_with_output()
        .map_err(|error| format!("unable to read sidecar response: {error}"))?;
    if !output.status.success() {
        return Err(match output.status.code() {
            Some(code) => format!("OSCA sidecar exited unsuccessfully with status {code}"),
            None => "OSCA sidecar exited unsuccessfully".to_string(),
        });
    }

    decode_response(&output.stdout)
}

fn apply_sidecar_profile_authorization(command: &mut Command, broker_owned_profile: Option<&str>) {
    if let Some(profile_root) = broker_owned_profile {
        command.env(BROKER_OWNED_PROFILE_ENV, profile_root);
    } else {
        command.env_remove(BROKER_OWNED_PROFILE_ENV);
    }
}

fn request_context(request_json: &str) -> Result<(String, Option<String>), String> {
    let request: Value = serde_json::from_str(request_json)
        .map_err(|error| format!("desktop request is invalid JSON: {error}"))?;
    let method = request
        .get("method")
        .and_then(Value::as_str)
        .ok_or_else(|| "desktop request method is missing".to_string())?
        .to_string();
    let profile_root = request
        .get("params")
        .and_then(Value::as_object)
        .and_then(|params| params.get("profile_root"))
        .and_then(Value::as_str)
        .map(normalize_profile_root);
    Ok((method, profile_root))
}

fn normalize_profile_root(profile_root: &str) -> String {
    let path = Path::new(profile_root);
    path.canonicalize()
        .unwrap_or_else(|_| PathBuf::from(path))
        .to_string_lossy()
        .into_owned()
}

fn is_profile_mutation(method: &str) -> bool {
    matches!(
        method,
        "watchlist.create"
            | "watchlist.rename"
            | "watchlist.delete"
            | "watchlist.asset.add"
            | "watchlist.asset.remove"
            | "watchlist.reorder"
            | "asset.recent.record"
            | "workbench.export.prepare"
            | "workbench.view.create"
            | "workbench.view.update"
            | "workbench.view.rename"
            | "workbench.view.delete"
    )
}

fn stable_profile_identity(profile_root: &str) -> u64 {
    profile_root
        .as_bytes()
        .iter()
        .fold(FNV_OFFSET_BASIS, |hash, byte| {
            (hash ^ u64::from(*byte)).wrapping_mul(FNV_PRIME)
        })
}

fn acquire_profile_session_lease(profile_root: &str) -> Result<ProfileSessionLease, String> {
    let identity = stable_profile_identity(profile_root);
    let directory = env::temp_dir().join("osca-desktop-session-locks");
    std::fs::create_dir_all(&directory)
        .map_err(|error| format!("unable to create profile-session lock directory: {error}"))?;
    let lock_path = directory.join(format!("{identity:016x}.lock"));
    let file = OpenOptions::new()
        .create(true)
        .read(true)
        .write(true)
        .truncate(false)
        .open(&lock_path)
        .map_err(|error| format!("unable to open profile-session lock: {error}"))?;
    let result = unsafe { flock(file.as_raw_fd(), LOCK_EX | LOCK_NB) };
    if result != 0 {
        return Err("profile is already open in another OSCA window or process".to_string());
    }
    Ok(ProfileSessionLease {
        profile_root: profile_root.to_string(),
        _file: file,
    })
}

fn response_succeeded(response_json: &str) -> Result<bool, String> {
    let response: Value = serde_json::from_str(response_json)
        .map_err(|error| format!("desktop response is invalid JSON: {error}"))?;
    Ok(response.get("status").and_then(Value::as_str) == Some("ok"))
}

fn override_window_profile(
    response_json: &str,
    method: &str,
    opened_profile: Option<&str>,
) -> Result<String, String> {
    if opened_profile.is_none() || !matches!(method, "desktop.bootstrap" | "profile.list") {
        return Ok(response_json.to_string());
    }
    let mut response: Value = serde_json::from_str(response_json)
        .map_err(|error| format!("desktop response is invalid JSON: {error}"))?;
    if response.get("status").and_then(Value::as_str) == Some("ok") {
        if let Some(result) = response.get_mut("result").and_then(Value::as_object_mut) {
            result.insert(
                "selected_profile".to_string(),
                Value::String(opened_profile.expect("opened profile checked").to_string()),
            );
        }
    }
    serde_json::to_string(&response)
        .map_err(|error| format!("unable to encode desktop response: {error}"))
}

fn sidecar_invocation(
    sidecar: Option<String>,
    python: Option<String>,
    bundled: Option<String>,
) -> (String, Vec<String>) {
    if let Some(executable) = sidecar {
        return (executable, Vec::new());
    }
    if let Some(interpreter) = python {
        return (
            interpreter,
            vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()],
        );
    }
    if let Some(executable) = bundled {
        return (executable, Vec::new());
    }
    (
        "python3".to_string(),
        vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()],
    )
}

fn bundled_sidecar_path(app: &tauri::AppHandle) -> Option<String> {
    let resource_dir = app.path().resource_dir().ok()?;
    resource_sidecar_path(&resource_dir)
}

fn resource_sidecar_path(resource_dir: &Path) -> Option<String> {
    let executable_name = if cfg!(target_os = "windows") {
        "osca-sidecar.exe"
    } else {
        "osca-sidecar"
    };
    let executable = resource_dir
        .join("binaries")
        .join("osca-sidecar-runtime")
        .join(executable_name);
    executable
        .is_file()
        .then(|| executable.to_string_lossy().into_owned())
}

fn validate_request_size(request_json: &str) -> Result<(), String> {
    if request_json.len() > MAX_MESSAGE_BYTES {
        return Err("desktop request exceeds 1 MiB".to_string());
    }
    Ok(())
}

fn decode_response(stdout: &[u8]) -> Result<String, String> {
    if stdout.len() > MAX_MESSAGE_BYTES {
        return Err("desktop response exceeds 1 MiB".to_string());
    }
    let response = std::str::from_utf8(stdout)
        .map_err(|error| format!("sidecar returned non-UTF-8 output: {error}"))?;
    let mut lines = response.lines().filter(|line| !line.trim().is_empty());
    let first = lines
        .next()
        .ok_or_else(|| "sidecar returned no response".to_string())?;
    if lines.next().is_some() {
        return Err("sidecar returned multiple responses for one request".to_string());
    }
    Ok(first.to_owned())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(BrokerState::default())
        .invoke_handler(tauri::generate_handler![desktop_request])
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::Destroyed) {
                window
                    .app_handle()
                    .state::<BrokerState>()
                    .release_window(window.label());
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running OSCA desktop");
}

#[cfg(test)]
mod tests {
    use super::{
        acquire_profile_session_lease, apply_sidecar_profile_authorization, decode_response,
        is_profile_mutation, override_window_profile, resource_sidecar_path, sidecar_invocation,
        stable_profile_identity, validate_request_size, BrokerState, BROKER_OWNED_PROFILE_ENV,
        MAX_MESSAGE_BYTES,
    };
    use std::ffi::OsStr;
    use std::fs;
    use std::path::PathBuf;
    use std::process::Command;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn unique_profile(name: &str) -> String {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos();
        format!(
            "/tmp/osca-session-test-{name}-{}-{unique}",
            std::process::id()
        )
    }

    fn unique_resource_root(name: &str) -> PathBuf {
        PathBuf::from(unique_profile(name))
    }

    #[test]
    fn executable_sidecar_override_receives_no_python_module_arguments() {
        let invocation = sidecar_invocation(Some("osca-sidecar".to_string()), None, None);
        assert_eq!(invocation, ("osca-sidecar".to_string(), Vec::new()));
    }

    #[test]
    fn python_override_runs_the_versioned_desktop_module() {
        let invocation = sidecar_invocation(None, Some("/tmp/osca-python".to_string()), None);
        assert_eq!(
            invocation,
            (
                "/tmp/osca-python".to_string(),
                vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()]
            )
        );
    }

    #[test]
    fn bundled_sidecar_is_used_without_development_overrides() {
        let invocation = sidecar_invocation(None, None, Some("/app/osca-sidecar".to_string()));
        assert_eq!(invocation, ("/app/osca-sidecar".to_string(), Vec::new()));
    }

    #[test]
    fn packaged_sidecar_is_resolved_from_resource_runtime() {
        let root = unique_resource_root("resource-runtime");
        let runtime = root.join("binaries").join("osca-sidecar-runtime");
        fs::create_dir_all(&runtime).expect("create runtime");
        let executable_name = if cfg!(target_os = "windows") {
            "osca-sidecar.exe"
        } else {
            "osca-sidecar"
        };
        let executable = runtime.join(executable_name);
        fs::write(&executable, b"test").expect("write executable fixture");

        assert_eq!(
            resource_sidecar_path(&root),
            Some(executable.to_string_lossy().into_owned())
        );
        fs::remove_dir_all(root).expect("remove runtime fixture");
    }

    #[test]
    fn default_sidecar_uses_python3_module_execution_as_last_resort() {
        let invocation = sidecar_invocation(None, None, None);
        assert_eq!(
            invocation,
            (
                "python3".to_string(),
                vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()]
            )
        );
    }

    #[test]
    fn broker_owned_profile_is_passed_only_to_authorized_sidecar() {
        let mut command = Command::new("python3");
        apply_sidecar_profile_authorization(&mut command, Some("/tmp/profile-a"));
        let owned = command
            .get_envs()
            .find(|(key, _)| *key == OsStr::new(BROKER_OWNED_PROFILE_ENV))
            .and_then(|(_, value)| value);
        assert_eq!(owned, Some(OsStr::new("/tmp/profile-a")));

        let mut unowned = Command::new("python3");
        apply_sidecar_profile_authorization(&mut unowned, None);
        let removed = unowned
            .get_envs()
            .find(|(key, _)| *key == OsStr::new(BROKER_OWNED_PROFILE_ENV));
        assert!(matches!(removed, Some((_, None))));
    }

    #[test]
    fn d5_workbench_writes_require_profile_ownership() {
        for method in [
            "workbench.export.prepare",
            "workbench.view.create",
            "workbench.view.update",
            "workbench.view.rename",
            "workbench.view.delete",
        ] {
            assert!(is_profile_mutation(method), "{method} must require ownership");
        }
        assert!(!is_profile_mutation("workbench.series.get"));
        assert!(!is_profile_mutation("workbench.analysis.get"));
        assert!(!is_profile_mutation("workbench.comparison.get"));
        assert!(!is_profile_mutation("workbench.view.list"));
        assert!(!is_profile_mutation("workbench.view.get"));
    }

    #[test]
    fn accepts_one_bounded_response_line() {
        let response = decode_response(b"{\"status\":\"ok\"}\n").expect("valid response");
        assert_eq!(response, "{\"status\":\"ok\"}");
    }

    #[test]
    fn rejects_multiple_response_lines() {
        let error = decode_response(b"{}\n{}\n").expect_err("multiple responses must fail");
        assert_eq!(error, "sidecar returned multiple responses for one request");
    }

    #[test]
    fn rejects_oversized_request_and_response() {
        let oversized = "x".repeat(MAX_MESSAGE_BYTES + 1);
        assert_eq!(
            validate_request_size(&oversized).expect_err("oversized request must fail"),
            "desktop request exceeds 1 MiB"
        );
        assert_eq!(
            decode_response(oversized.as_bytes()).expect_err("oversized response must fail"),
            "desktop response exceeds 1 MiB"
        );
    }

    #[test]
    fn profile_lock_identity_is_stable() {
        assert_eq!(
            stable_profile_identity("/tmp/profile-a"),
            stable_profile_identity("/tmp/profile-a")
        );
        assert_ne!(
            stable_profile_identity("/tmp/profile-a"),
            stable_profile_identity("/tmp/profile-b")
        );
    }

    #[test]
    fn profile_session_lease_excludes_a_second_window_owner() {
        let profile = unique_profile("exclusive");
        let first = acquire_profile_session_lease(&profile).expect("first lease");
        let state = BrokerState::default();
        state.commit_lease("window-a", first).expect("commit lease");
        let error = acquire_profile_session_lease(&profile)
            .err()
            .expect("second lease must fail");
        assert!(error.contains("already open"));
        assert!(state
            .owns_profile("window-a", &profile)
            .expect("owner check"));
    }

    #[test]
    fn selection_without_open_ownership_cannot_mutate_profile() {
        let profile = unique_profile("selection-only");
        let state = BrokerState::default();
        let error = state
            .require_owner("window-b", &profile)
            .expect_err("selection alone must not grant mutation authority");
        assert!(error.contains("open and own"));
    }

    #[test]
    fn releasing_owner_allows_another_window_to_acquire_profile() {
        let profile = unique_profile("release");
        let first = acquire_profile_session_lease(&profile).expect("first lease");
        let state = BrokerState::default();
        state.commit_lease("window-a", first).expect("commit lease");
        state.release_window("window-a");

        let second = acquire_profile_session_lease(&profile).expect("lease after release");
        state
            .commit_lease("window-b", second)
            .expect("commit second lease");
        assert!(state
            .owns_profile("window-b", &profile)
            .expect("second owner check"));
    }

    #[test]
    fn independent_windows_keep_independent_open_profile_context() {
        let profile_a = unique_profile("a");
        let profile_b = unique_profile("b");
        let state = BrokerState::default();
        state
            .commit_lease(
                "window-a",
                acquire_profile_session_lease(&profile_a).expect("profile A lease"),
            )
            .expect("commit profile A");
        state
            .commit_lease(
                "window-b",
                acquire_profile_session_lease(&profile_b).expect("profile B lease"),
            )
            .expect("commit profile B");

        assert_eq!(
            state.opened_profile("window-a").expect("window A profile"),
            Some(profile_a)
        );
        assert_eq!(
            state.opened_profile("window-b").expect("window B profile"),
            Some(profile_b)
        );
    }

    #[test]
    fn bootstrap_selected_profile_is_overridden_by_window_owned_profile() {
        let response = r#"{"status":"ok","result":{"selected_profile":"/other"}}"#;
        let updated = override_window_profile(response, "desktop.bootstrap", Some("/owned"))
            .expect("override");
        assert!(updated.contains("\"selected_profile\":\"/owned\""));
    }
}
