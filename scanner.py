import subprocess
import re
import json

pc_to_ip_mapping: dict[str, str] = {}
HOSTS_FILE: str = "hosts.json"


def validate_ipv4(ip: str) -> bool:
    """Validate IPv4 address format (e.g., '192.168.1.1')"""
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))


def validate_cidr_prefix(prefix: str) -> bool:
    """Validate CIDR prefix (e.g., '24', '16', '32')"""
    pattern = r"^([0-9]|[12][0-9]|3[0-2])$"
    return bool(re.match(pattern, prefix))


class SSHScanner:
    def __init__(
        self, user: str = "spravce", ssh_timeout: int = 5, nmap_timing: str = "-T4"
    ) -> None:
        self.user: str = user
        self.execute_remote_timeout: int = ssh_timeout
        self.nmap_timing: str = nmap_timing

    def _network_ip_validation(self) -> str:
        while True:
            ip: str = input("Input subnet ip : ").strip()
            if validate_ipv4(ip):
                return ip
            print(f"Invalid IP address: {ip}. Please try again.")

    def _network_mask_validation(self) -> str:
        while True:
            mask: str = input("Enter subnet mask (prefix 0-32): ").strip()
            if validate_cidr_prefix(mask):
                return mask
            print(
                f"Invalid CIDR prefix: {mask}. Must be between 0-32. Please try again."
            )

    def scan(self, network_ip: str | None = None, mask: str | None = None) -> str:
        if not network_ip:
            network_ip = self._network_ip_validation()
        if not mask:
            mask = self._network_mask_validation()
        cmd: list[str] = [
            "nmap",
            self.nmap_timing,
            "-p22",
            "-oG",
            "-",
            f"{network_ip}/{mask}",
        ]
        return subprocess.check_output(cmd, text=True)

    def parse_ips(self, scan_output: str) -> list[str]:
        ips: list[str] = []
        for line in scan_output.splitlines():
            if "Ports: 22/open" in line:
                ips.append(line.split()[1])

        return ips

    def get_hostname(self, ip: str) -> str | None:
        target: str = f"{self.user}@{ip}"
        cmd: list[str] = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            target,
            "hostname",
        ]
        try:
            out: str = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=self.execute_remote_timeout + 1,
            )
            return out.strip()
        except Exception as e:
            print(e)
            return None

    def is_hosts_file_exists(self) -> bool:
        try:
            with open(HOSTS_FILE, "r", encoding="utf-8"):
                pass
            return True
        except Exception:
            return False

    def get_hosts_from_file(self) -> dict[str, str]:
        try:
            with open(HOSTS_FILE, "r", encoding="utf-8") as f:
                data: dict[str, str] = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading hosts file: {e}")
            return {}

    def save_hosts_to_file(self, mapping: dict[str, str]) -> None:
        with open(HOSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=4)

    def get_mapping_pc_ip(self, ips: list[str]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for ip in ips:
            print(f"Checking {ip} ...", end=" ", flush=True)
            name: str | None = self.get_hostname(ip)
            if name:
                print(f"OK -> {name}")
                mapping[name] = ip
            else:
                print("no response / auth failed")

        self.save_hosts_to_file(mapping)
        return mapping

    def print_hosts(self) -> None:
        print(f"\nDiscovered {len(pc_to_ip_mapping)} hosts.")
        for ip, name in pc_to_ip_mapping.items():
            print(f"{ip}\t{name}")

    def config(self):
        pass

    def load(self, force_scan: bool):
        if not force_scan and self.is_hosts_file_exists():
            print("Loading hosts from file...")
            pc_to_ip_mapping.clear()
            pc_to_ip_mapping.update(self.get_hosts_from_file())
            self.print_hosts()
            return

    def run(self, force_scan: bool = False, network_ip: str | None = None, mask: str | None = None) -> None:
        global pc_to_ip_mapping

        if not force_scan and self.is_hosts_file_exists():
            print("Loading hosts from file...")
            pc_to_ip_mapping.clear()
            pc_to_ip_mapping.update(self.get_hosts_from_file())
            self.print_hosts()
            return

        raw = self.scan(network_ip, mask)
        ips = self.parse_ips(raw)
        if not ips:
            print("No hosts with port 22 open found.")
            return

        pc_to_ip_mapping.clear()
        pc_to_ip_mapping.update(self.get_mapping_pc_ip(ips))
        self.print_hosts()
