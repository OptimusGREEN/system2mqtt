# Running as a Service

This page explains how to configure system2mqtt to start automatically on boot using **systemd** (Linux) or **LaunchAgent** (macOS).

---

## Linux — systemd

### 1. Edit the service file

A template service file is included in `service examples/linux/s2m.service`. Copy it and edit it to match your setup:

```sh
cp "service examples/linux/s2m.service" /tmp/s2m.service
nano /tmp/s2m.service
```

Update the following fields in the `[Service]` section:

| Field | Default | Update to |
|-------|---------|-----------|
| `User` | `john` | Your Linux username |
| `ExecStart` | `/home/john/system2mqtt/run.py` | Absolute path to `run.py` in your clone |

A typical edited service file:

```ini
[Unit]
Description=System2Mqtt Service
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=pi
Restart=on-failure
RestartSec=2s
ExecStart=python3 /home/pi/system2mqtt/run.py

[Install]
WantedBy=multi-user.target
```

### 2. Install the service

```sh
sudo cp /tmp/s2m.service /etc/systemd/system/s2m.service
sudo systemctl daemon-reload
```

### 3. Enable and start

```sh
sudo systemctl enable s2m     # Start automatically on boot
sudo systemctl start s2m      # Start now
```

### 4. Check status

```sh
sudo systemctl status s2m
```

### Common systemctl commands

| Command | Description |
|---------|-------------|
| `sudo systemctl start s2m` | Start the service |
| `sudo systemctl stop s2m` | Stop the service |
| `sudo systemctl restart s2m` | Restart the service |
| `sudo systemctl status s2m` | Show current status and recent logs |
| `sudo systemctl enable s2m` | Enable automatic start on boot |
| `sudo systemctl disable s2m` | Disable automatic start on boot |
| `journalctl -u s2m -f` | Follow service logs in real time |

---

## macOS — LaunchAgent

### 1. Edit the plist file

A template LaunchAgent property list is included at `service examples/macos/com.optimusgreen.s2m.plist`. Copy it and edit it:

```sh
cp "service examples/macos/com.optimusgreen.s2m.plist" /tmp/com.optimusgreen.s2m.plist
nano /tmp/com.optimusgreen.s2m.plist
```

Update the `ProgramArguments` path to the absolute path to `run.py`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.optimusgreen.s2m</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/yourname/system2mqtt/run.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

### 2. Install the LaunchAgent

```sh
cp /tmp/com.optimusgreen.s2m.plist ~/Library/LaunchAgents/com.optimusgreen.s2m.plist
```

### 3. Load the agent

```sh
launchctl load ~/Library/LaunchAgents/com.optimusgreen.s2m.plist
```

The agent will start immediately and also start automatically when you log in.

### 4. Check status

```sh
launchctl list | grep s2m
```

A non-zero PID in the output means the agent is running.

### Common launchctl commands

| Command | Description |
|---------|-------------|
| `launchctl load ~/Library/LaunchAgents/com.optimusgreen.s2m.plist` | Load and start the agent |
| `launchctl unload ~/Library/LaunchAgents/com.optimusgreen.s2m.plist` | Stop and unload the agent |
| `launchctl start com.optimusgreen.s2m` | Start a loaded agent |
| `launchctl stop com.optimusgreen.s2m` | Stop a running agent |
| `launchctl list \| grep s2m` | Check if agent is running |

---

## Notes

- Make sure `s2m.conf` exists and contains at least `COMPUTER_NAME` before starting the service.
- If system2mqtt crashes, both systemd (`Restart=on-failure`) and the `run.py` watchdog will attempt to restart it.
- The `run.py` watchdog also sets up the Python virtual environment on first run, so there is no need to pre-install dependencies.
