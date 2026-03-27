# Proxmox Monitoring

system2mqtt can monitor a [Proxmox VE](https://www.proxmox.com/en/proxmox-virtual-environment/overview) node by querying its REST API. This is particularly useful when running system2mqtt inside a Docker container on a separate machine.

---

## How It Works

When `PVE_SYSTEM=True`, system2mqtt connects to the Proxmox API instead of reading local system metrics. It retrieves:

- **CPU usage** from the Proxmox node status endpoint
- **Memory usage** from the Proxmox node status endpoint
- **Storage usage** for each storage configured on the node

The collected data is published to MQTT using the same topic structure as bare-metal mode.

---

## Configuration

Add the following to your `s2m.conf`:

```ini
COMPUTER_NAME=MyPveNode

PVE_SYSTEM=True
PVE_HOST=192.168.1.50       # IP or hostname of the Proxmox server
PVE_NODE_NAME=pve           # Node name as shown in the Proxmox UI (default: pve)
PVE_USER=root@pam           # Proxmox user (default: root@pam)
PVE_PASSWORD=mysecretpw     # Proxmox user password (required)
```

You also need standard MQTT and optional Home Assistant settings:

```ini
MQTT_HOST=192.168.1.100
HA_DISCOVERY=True           # Optional: auto-register entities in Home Assistant
```

---

## Proxmox User Permissions

It is good practice to create a dedicated, read-only Proxmox user for monitoring rather than using `root@pam`.

### Creating a monitoring user in Proxmox

1. In the Proxmox UI, go to **Datacenter → Permissions → Users** and create a new user (e.g. `monitor@pve`).
2. Go to **Datacenter → Permissions → Roles** and verify or create a role with at least `Sys.Audit` and `Datastore.Audit` privileges.
3. Go to **Datacenter → Permissions** and assign the role to the user at the `/` path.

Then update your config:

```ini
PVE_USER=monitor@pve
PVE_PASSWORD=monitorpassword
```

---

## MQTT Topics (Proxmox Mode)

When running in Proxmox mode the same MQTT topic structure applies:

| Topic | Description |
|-------|-------------|
| `<base>/cpu/usage` | Node CPU usage (%) |
| `<base>/memory` | Node memory usage (%) |
| `<base>/disks/storage/<label>` | Storage pool usage (%) |
| `<base>/disks/mount/<label>` | Storage pool active state (`mounted` / `unmounted`) |
| `<base>/LWT` | Availability (`online` / `offline`) |

---

## Docker Deployment (Recommended for Proxmox)

The Docker image is optimised for Proxmox API monitoring. See the [Docker Deployment](docker.md) page for full instructions.

**Quick start:**

```sh
# Create a data directory for your config
mkdir data
cp docker/s2m.conf data/s2m.conf

# Edit data/s2m.conf with your Proxmox and MQTT settings
nano data/s2m.conf

# Start the container
cd docker
docker-compose up -d
```

---

## Notes

- The Proxmox API uses self-signed TLS certificates by default. The `optimox.py` library disables SSL verification (`verify=False`) to handle this. For production deployments, consider configuring a trusted certificate on your Proxmox node.
- CPU temperature is **not** available in Proxmox API mode.
- Argon ONE fan speed is **not** available in Proxmox API mode.
