# Docker Deployment

system2mqtt can be run in a Docker container. The Docker image is primarily designed for **Proxmox API monitoring** — it does not have access to the host's hardware sensors, so bare-metal CPU/memory monitoring is not available in a standard Docker deployment.

> **Note:** The Docker image is available on [Docker Hub](https://hub.docker.com/repository/docker/optimusgreen/system2mqtt) as `optimusgreen/system2mqtt`.

---

## Quick Start

### 1. Create a configuration directory

```sh
mkdir -p ~/system2mqtt/data
```

### 2. Create your configuration file

Copy the Docker-specific example:

```sh
cp docker/s2m.conf ~/system2mqtt/data/s2m.conf
```

Or create a new one:

```sh
cat > ~/system2mqtt/data/s2m.conf << 'EOF'
COMPUTER_NAME=MyPveNode

MQTT_HOST=192.168.1.100
#MQTT_USER=myuser
#MQTT_PASSWORD=mypassword

PVE_SYSTEM=True
PVE_HOST=192.168.1.50
PVE_NODE_NAME=pve
PVE_USER=root@pam
PVE_PASSWORD=mysecretpassword

HA_DISCOVERY=True
EOF
```

### 3. Create a docker-compose.yaml

```yaml
version: "2"
services:
  system2mqtt:
    image: optimusgreen/system2mqtt:latest
    container_name: system2mqtt
    restart: unless-stopped
    volumes:
      - ./data:/config
```

### 4. Start the container

```sh
docker-compose up -d
```

### 5. Check the logs

```sh
docker-compose logs -f
```

---

## Configuration

The container expects your `s2m.conf` to be placed in the `/config` volume. The container runs:

```sh
python3 /system2mqtt/run.py /config/s2m.conf
```

Any changes to `s2m.conf` require a container restart to take effect:

```sh
docker-compose restart
```

---

## Building the Image Locally

If you want to build the image yourself from the included `Dockerfile`:

```sh
cd docker
docker build -t my-system2mqtt .
```

Then update your `docker-compose.yaml` to use the local image:

```yaml
services:
  system2mqtt:
    image: my-system2mqtt
    ...
```

---

## Docker and Bare-Metal Monitoring

The standard Docker image does **not** support bare-metal system monitoring because:

- It cannot access the host's `/sys/class/thermal` for CPU temperature.
- It cannot access the host's disks via `psutil` inside the container.

If you specifically need to monitor the Docker host machine:

- Run system2mqtt directly on the host instead (see [Getting Started](getting-started.md)).
- Or, use `--privileged` mode and mount host filesystems — this is an advanced configuration not officially supported.

---

## Updating

Pull the latest image and recreate the container:

```sh
docker-compose pull
docker-compose up -d
```
