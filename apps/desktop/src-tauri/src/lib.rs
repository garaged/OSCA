use std::env;
use std::io::Write;
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const MAX_MESSAGE_BYTES: usize = 1_048_576;
const SIDECAR_TIMEOUT: Duration = Duration::from_secs(15);
const SIDECAR_POLL_INTERVAL: Duration = Duration::from_millis(25);

#[tauri::command]
fn desktop_request(request_json: String) -> Result<String, String> {
    validate_request_size(&request_json)?;

    let (program, args) = sidecar_invocation(
        env::var("OSCA_DESKTOP_SIDECAR").ok(),
        env::var("OSCA_DESKTOP_PYTHON").ok(),
    );
    let mut command = Command::new(program);
    command.args(args);

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

fn sidecar_invocation(sidecar: Option<String>, python: Option<String>) -> (String, Vec<String>) {
    match sidecar {
        Some(executable) => (executable, Vec::new()),
        None => (
            python.unwrap_or_else(|| "python3".to_string()),
            vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()],
        ),
    }
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
        .invoke_handler(tauri::generate_handler![desktop_request])
        .run(tauri::generate_context!())
        .expect("error while running OSCA desktop");
}

#[cfg(test)]
mod tests {
    use super::{decode_response, sidecar_invocation, validate_request_size, MAX_MESSAGE_BYTES};

    #[test]
    fn executable_sidecar_override_receives_no_python_module_arguments() {
        let invocation = sidecar_invocation(Some("osca-sidecar".to_string()), None);
        assert_eq!(invocation, ("osca-sidecar".to_string(), Vec::new()));
    }

    #[test]
    fn python_override_runs_the_versioned_desktop_module() {
        let invocation = sidecar_invocation(None, Some("/tmp/osca-python".to_string()));
        assert_eq!(
            invocation,
            (
                "/tmp/osca-python".to_string(),
                vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()]
            )
        );
    }

    #[test]
    fn default_sidecar_uses_python3_module_execution() {
        let invocation = sidecar_invocation(None, None);
        assert_eq!(
            invocation,
            (
                "python3".to_string(),
                vec!["-m".to_string(), "osca.desktop_api.stdio".to_string()]
            )
        );
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
}
