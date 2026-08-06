use std::env;
use std::io::Write;
use std::process::{Command, Stdio};

#[tauri::command]
fn desktop_request(request_json: String) -> Result<String, String> {
    if request_json.len() > 1_048_576 {
        return Err("desktop request exceeds 1 MiB".to_string());
    }

    let sidecar = env::var("OSCA_DESKTOP_SIDECAR").unwrap_or_else(|_| "python3".to_string());
    let mut command = Command::new(sidecar);
    if env::var("OSCA_DESKTOP_SIDECAR").is_err() {
        command.args(["-m", "osca.desktop_api.stdio"]);
    }

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

    let output = child
        .wait_with_output()
        .map_err(|error| format!("unable to read sidecar response: {error}"))?;
    if !output.status.success() {
        return Err(format!(
            "OSCA sidecar exited unsuccessfully: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }

    let response = String::from_utf8(output.stdout)
        .map_err(|error| format!("sidecar returned non-UTF-8 output: {error}"))?;
    response
        .lines()
        .next()
        .map(str::to_owned)
        .ok_or_else(|| "sidecar returned no response".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![desktop_request])
        .run(tauri::generate_context!())
        .expect("error while running OSCA desktop");
}
