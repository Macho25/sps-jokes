import subprocess


class SSHConnection:
    def __init__(self, user: str = "spravce", timeout: int = 5) -> None:
        self.user: str = user
        self.timeout: int = timeout
        self.target: str = ""

    def connect(self, ip: str):
        self.target = f"{self.user}@{ip}"

    def execute(self, cmd: str) -> str:
        result = subprocess.run(
            ["ssh", self.target, cmd],
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        return result.stdout

    def execute_quiet(self, cmd: str) -> None:
        subprocess.run(
            ["ssh", self.target, cmd],
            stderr=subprocess.DEVNULL,
            timeout=self.timeout,
        )

    def get_hostname(self) -> str | None:
        try:
            result = subprocess.run(
                ["ssh", self.target, "hostname"],
                capture_output=True,
                text=True,
                timeout=self.timeout + 1,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def scp(self, local_path: str, remote_path: str) -> None:
        subprocess.run(
            ["scp", local_path, f"{self.target}:{remote_path}"],
            stderr=subprocess.DEVNULL,
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.target = ""
