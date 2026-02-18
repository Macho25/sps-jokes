import subprocess
import re


pc_to_ip_mapping: dict[str, str] = {}


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

    def scan(self) -> str:
        network_ip: str = self._network_ip_validation()
        mask: str = self._network_mask_validation()
        cmd = ["nmap", self.nmap_timing, "-p22", "-oG", "-", f"{network_ip}/{mask}"]
        return subprocess.check_output(cmd, text=True)

    def parse_ips(self, scan_output: str) -> list[str]:
        ips: list[str] = []
        for line in scan_output.splitlines():
            if "Ports: 22/open" in line:
                ips.append(line.split()[1])

        return ips

    def get_hostname(self, ip: str) -> str | None:
        target = f"{self.user}@{ip}"
        cmd = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.execute_remote_timeout}",
            target,
            "hostname",
        ]
        try:
            out = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=self.execute_remote_timeout + 1,
            )
            return out.strip()
        except Exception as e:
            print(e)
            return None

    def get_mappping_ip_pc(self, ips: list[str]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for ip in ips:
            print(f"Checking {ip} ...", end=" ", flush=True)
            name = self.get_hostname(ip)
            if name:
                print(f"OK -> {name}")
                mapping[ip] = name
            else:
                print("no response / auth failed")

        with open("hosts.txt", "w", encoding="utf-8") as f:
            for ip, name in mapping.items():
                f.write(f"{ip} {name}\n")
        return mapping

    def run(self):
        global pc_to_ip_mapping
        raw = self.scan()
        ips = self.parse_ips(raw)
        if not ips:
            print("No hosts with port 22 open found.")
            return
        pc_to_ip_mapping = self.get_mappping_ip_pc(ips)
        print(f"\nDiscovered {len(pc_to_ip_mapping)} hosts.")
        for ip, name in pc_to_ip_mapping.items():
            print(f"{ip}\t{name}")
