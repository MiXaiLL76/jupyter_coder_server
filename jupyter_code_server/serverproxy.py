def setup_jupyter_code_server():
    return {
        "command": [
            "code-server",
            "--auth=none",
            "--app-name='Remote VSCode Server'",
            "--disable-telemetry",
            "--disable-update-check",
            "--disable-workspace-trust",
            "--bind-addr=0.0.0.0:{port}",
        ],
        "timeout": 10,
        "launcher_entry": {"title": "VS Code"},
    }
