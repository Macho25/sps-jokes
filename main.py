#!/usr/bin/env python3
from scanner import SSHScanner, pc_to_ip_mapping, validate_ipv4
from ssh_connection import SSHConnection
from pranks import Speech
from reverse_shell import RSHConnection


class Jokes:
    """
    GNOME pranks over SSH.
    Each prank has apply() and reset() methods.
    """

    def __init__(self, user: str) -> None:
        self.user: str = user
        self.target_pc: str = ""
        self.prank_index: int = 0
        self.ssh_connection: SSHConnection = SSHConnection(user=user)
        self.speech: Speech = Speech()

        self.menu = [
            ("Invert mouse buttons", self.invert_mouse_buttons),
            ("send_fake_notifications", self.send_fake_notifications),
            ("Cursor size", self.cursor_size),
            ("Random cursor size", self.random_cursor_size),
            ("Animations / primary paste", self.animations),
            ("Wallpaper", self.wallpaper),
            ("Cursor blink", self.cursor_blink),
            ("Natural scroll", self.natural_scroll),
            ("Keyboard delay", self.keyboard_delay),
            ("Speech", self.speech),
        ]

    def _network_ip_validation(self) -> str:
        while True:
            ip: str = input("Input target ip : ").strip()
            if validate_ipv4(ip):
                return ip
            print(f"Invalid IP address: {ip}. Please try again.")

    def execute_remote(self, ip: str, cmd: str) -> None:
        self.ssh_connection.connect(ip)
        try:
            self.ssh_connection.execute(cmd)
        except Exception as e:
            print(e)
            return

    # ****************************************************************************************************
    #                   Invidual pranks
    # ****************************************************************************************************

    def invert_mouse_buttons(self, ip: str, reset: bool = False) -> None:
        cmd: str = (
            "gsettings reset org.gnome.desktop.peripherals.mouse left-handed"
            if reset
            else "gsettings set org.gnome.desktop.peripherals.mouse left-handed true"
        )
        self.execute_remote(ip, cmd)

    def send_fake_notifications(self, ip: str) -> None:
        self.execute_remote(
            ip, "notify-send 'System Error' 'Critical kernel module failure detected'"
        )
        self.execute_remote(
            ip,
            "notify-send -u critical 'WARNING' 'Unauthorized keyboard activity detected'",
        )

    def cursor_size(self, ip: str, reset: bool = False) -> None:
        cmd: str = (
            "gsettings reset org.gnome.desktop.interface cursor-size"
            if reset
            else "gsettings set org.gnome.desktop.interface cursor-size 128"
        )
        self.execute_remote(ip, cmd)

    def random_cursor_size(self, ip: str, reset: bool = False) -> None:
        import random

        if reset:
            reset_cmd_size: str = (
                "gsettings reset org.gnome.desktop.interface cursor-size"
            )
            reset_cmd_time: str = (
                "gsettings reset org.gnome.desktop.interface cursor-blink-time"
            )
            self.execute_remote(ip, reset_cmd_size)
            self.execute_remote(ip, reset_cmd_time)
        else:
            size: int = random.randint(24, 256)
            time_ms: int = 500
            set_cmd_size: str = (
                f"gsettings set org.gnome.desktop.interface cursor-size {size}"
            )
            set_cmd_time: str = (
                f"gsettings set org.gnome.desktop.interface cursor-blink-time {time_ms}"
            )
            self.execute_remote(ip, set_cmd_size)
            self.execute_remote(ip, set_cmd_time)

    def animations(self, ip: str, reset: bool = False) -> None:
        cmd: str = (
            "gsettings reset org.gnome.desktop.interface enable-animations"
            if reset
            else "gsettings set org.gnome.desktop.interface enable-animations true"
        )
        self.execute_remote(ip, cmd)
        cmd2: str = (
            "gsettings reset org.gnome.desktop.interface gtk-enable-primary-paste"
            if reset
            else "gsettings set org.gnome.desktop.interface gtk-enable-primary-paste false"
        )
        self.execute_remote(ip, cmd2)

    # ****************************************************************************************************
    #                   Wallpaper prank
    # ****************************************************************************************************

    def _validate_wallpaper_path(self) -> str:
        while True:
            wallpaper_path: str = input("Enter wallpaper path : ")
            try:
                with open(wallpaper_path, "r"):
                    pass
                return wallpaper_path
            except Exception as e:
                print(e)

    def wallpaper(self, ip: str, reset: bool = False, path: str | None = None) -> None:
        self.ssh_connection.connect(ip)

        if reset:
            reset_cmds: list[str] = [
                "gsettings reset org.gnome.desktop.background picture-uri",
                "gsettings reset org.gnome.desktop.background picture-uri-dark",
            ]
            for c in reset_cmds:
                self.ssh_connection.execute_quiet(c)
        else:
            wallpaper_path = path
            if wallpaper_path is None:
                print("Wrong wallpaper path")
                return
            remote_path = "/tmp/wallpaper.jpg"
            self.ssh_connection.scp(wallpaper_path, remote_path)
            set_cmd = f'gsettings set org.gnome.desktop.background picture-uri "file://{remote_path}"'
            self.ssh_connection.execute_quiet(set_cmd)

    def cursor_blink(self, ip: str, reset: bool = False) -> None:
        cmd: str = (
            "gsettings reset org.gnome.desktop.interface cursor-blink"
            if reset
            else "gsettings set org.gnome.desktop.interface cursor-blink true"
        )
        self.execute_remote(ip, cmd)
        cmd2: str = (
            "gsettings reset org.gnome.desktop.interface cursor-blink-time"
            if reset
            else "gsettings set org.gnome.desktop.interface cursor-blink-time 300"
        )
        self.execute_remote(ip, cmd2)

    def natural_scroll(self, ip: str, reset: bool = False) -> None:
        cmd: str = (
            "gsettings reset org.gnome.desktop.peripherals.mouse natural-scroll"
            if reset
            else "gsettings set org.gnome.desktop.peripherals.mouse natural-scroll true"
        )
        self.execute_remote(ip, cmd)

    def keyboard_delay(self, ip: str, reset: bool = False) -> None:
        # TODO
        # here and in the  functions above can be used like
        # cmd and just reset/set and value for it, so
        # it dont need to be two long strings, more clean
        cmd: str = (
            "gsettings reset org.gnome.desktop.peripherals.keyboard delay"
            if reset
            else "gsettings set org.gnome.desktop.peripherals.keyboard delay 1000"
        )
        self.execute_remote(ip, cmd)

    # def speech(self, ip: str) -> None:
    #     self.execute_remote(ip, "spd-say 'Hello. I am inside the machine.'")

    def get_target_pc(self) -> None:
        global pc_to_ip_mapping
        while True:
            self.target_pc = input("Write pc hostname : ")
            if self.target_pc in pc_to_ip_mapping:
                return

    def get_valid_prank_index(self) -> int:
        while True:
            choice: str = input("Enter the number of the prank to run: ")
            if not choice.isdigit():
                print("Invalid choice. Please enter a number.")
                continue
            choice_int = int(choice)
            if not (1 <= choice_int <= len(self.menu)):
                print("Invalid choice")
                continue
            return choice_int - 1

    def print_pranks(self) -> None:
        print("Available pranks:")
        for i, name in enumerate(self.menu, 1):
            print(f"{i}) {name[0]}")

    def get_prank(self) -> None:
        self.prank_index = self.get_valid_prank_index()

    # ****************************************************************************************************
    #                   Wallpaper class
    # ****************************************************************************************************

    # just preparing class for future use
    # and also make every method as
    # class method cuz I dont need more
    # instance of wallpaper
    #
    # class Wallpaper:
    #     def __init__(self, ip: str) -> None:
    #         self.ip: str = ip
    #         self.wallpaper_path: str = ""
    #
    #     def _validate_wallpaper_path(self):
    #         while True:
    #             self.wallpaper_path = input("Enter wallpaper path : ")
    #             try:
    #                 with open(self.wallpaper_path, "r"):
    #                     pass
    #                 return
    #             except Exception as e:
    #                 print(e)
    #
    #     def set(self):
    #         self._validate_wallpaper_path()
    #
    #     def reset(self):
    #         pass

    # ****************************************************************************************************
    #                   Start of the program
    # ****************************************************************************************************
    def run(self) -> None:
        global pc_to_ip_mapping
        # TODO
        # refractor this function

        ip: str = pc_to_ip_mapping[self.target_pc]

        prank_name, prank_func = self.menu[self.prank_index]

        reset: bool = False
        if prank_name not in [
            "send_fake_notifications",
            "Speech",
            "Random cursor size",
        ]:
            resp: str = (
                input("Do you want to reset instead of apply? (y/N): ").strip().lower()
            )
            reset = resp == "y"
        # Handle Speech specially since it uses Prank interface
        if prank_name == "Speech":
            self.speech.setup()
            self.speech.run(self.execute_remote, ip)
            print(f"{prank_name} executed on {ip}.")
            return
        elif prank_name == "Wallpaper":
            if not reset:
                wallpaper_path: str = self._validate_wallpaper_path()
                prank_func(ip, reset=reset, path=wallpaper_path)
            else:
                prank_func(ip, reset=reset)
        elif prank_name == "send_fake_notifications":
            prank_func(ip)
        else:
            prank_func(ip, reset=reset)

        print(f"{prank_name} executed on {ip}.")


joke = Jokes("spravce")

scanner = SSHScanner(user="spravce", ssh_timeout=5)
scanner_config: dict[str, str] = {}


def scan():
    while True:
        sub_cmd: str = input("scan> ")

        match sub_cmd:
            case s if "setup" in s:
                network_ip = scanner._network_ip_validation()
                mask = scanner._network_mask_validation()
                scanner_config["network_ip"] = network_ip
                scanner_config["mask"] = mask
                print(f"Config saved: {network_ip}/{mask}")

            case s if "load" in s:
                scanner.run(force_scan=False)

            case s if "run" in s:
                network_ip = scanner_config.get("network_ip")
                mask = scanner_config.get("mask")
                if network_ip and mask:
                    scanner.run(force_scan=True, network_ip=network_ip, mask=mask)
                else:
                    print("No config found. Use 'scan setup' first.")

            case s if "exit" in s:
                return

            case _:
                print("Usage: scan [setup|load|run]")


def main():
    user_cmd: str = input("> ")

    match user_cmd:
        case cmd if "scan" in cmd:
            scan()

        case cmd if "list" in cmd:
            joke.print_pranks()

        case cmd if "prank" in cmd:
            joke.print_pranks()
            joke.get_prank()

        case cmd if "target" in cmd:
            scanner.print_hosts()
            joke.get_target_pc()

        case cmd if "run" in cmd:
            joke.run()

        case cmd if "hosts" in cmd:
            # scanner.print_hosts()
            pass

        case cmd if "status" in cmd:
            # joke.status
            # prints current target, prank
            # for quick check
            pass

        case cmd if "rsh" in cmd:
            my_ip: str = input("Your ip: ")
            rsh_connection = RSHConnection(my_ip)
            rsh_connection.deploy(joke.target_pc)

        case _:
            print("Help: [scan|list|prank|target|run|hosts|status|rsh]")
            return


if __name__ == "__main__":
    while True:
        main()
