#!/usr/bin/env python3
from scanner import *


class Jokes:
    """
    GNOME pranks over SSH.
    Each prank has apply() and reset() methods.
    """

    def __init__(
        self, user: str, display: str = ":0", dbus_path: str | None = None
    ) -> None:
        self.user: str = user
        self.display: str = display
        self.dbus_path: str = dbus_path or "/run/user/1000/bus"
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
        """Run a command remotely with correct DISPLAY and DBUS"""
        full_cmd: str = f"export DISPLAY={self.display}; export DBUS_SESSION_BUS_ADDRESS={self.dbus_path}; {cmd}"
        subprocess.run(["ssh", f"{self.user}@{ip}", full_cmd])

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
            reset_cmd_size: str = "gsettings reset org.gnome.desktop.interface cursor-size"
            reset_cmd_time: str = "gsettings reset org.gnome.desktop.interface cursor-blink-time"
            self.execute_remote(ip, reset_cmd_size)
            self.execute_remote(ip, reset_cmd_time)
        else:
            size: int = random.randint(24, 256)
            time_ms: int = 500
            set_cmd_size: str = f"gsettings set org.gnome.desktop.interface cursor-size {size}"
            set_cmd_time: str = f"gsettings set org.gnome.desktop.interface cursor-blink-time {time_ms}"
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
        if reset:
            reset_cmds: list[str] = [
                "gsettings reset org.gnome.desktop.background picture-uri",
                "gsettings reset org.gnome.desktop.background picture-uri-dark",
            ]
            cmds = reset_cmds
        else:
            wallpaper_path = path or "/home/USER/Pictures/troll.jpg"
            set_cmds: list[str] = [
                f'gsettings set org.gnome.desktop.background picture-uri "file://{wallpaper_path}"'
            ]
            cmds = set_cmds
        for c in cmds:
            self.execute_remote(ip, c)

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

    def speech(self, ip: str) -> None:
        self.execute_remote(ip, "spd-say 'Hello. I am inside the machine.'")

    def get_pc(self) -> str:
        global pc_to_ip_mapping
        while True:
            pc: str = input("Write pc hostname : ")
            if pc in pc_to_ip_mapping:
                return pc

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
        self.print_pranks()

        choice: int = self.get_valid_prank_index()

        target_pc: str = self.get_pc()

        ip: str = pc_to_ip_mapping[target_pc]

        prank_name, prank_func = self.menu[choice]

        reset: bool = False
        if prank_name not in ["send_fake_notifications", "Speech", "Random cursor size"]:
            resp: str = (
                input("Do you want to reset instead of apply? (y/N): ").strip().lower()
            )
            reset = resp == "y"

        if prank_name == "Wallpaper":
            if not reset:
                wallpaper_path: str = self._validate_wallpaper_path()
                prank_func(ip, reset=reset, path=wallpaper_path)  # pyright: ignore[reportCallIssue]
            else:
                prank_func(ip, reset=reset)  # pyright: ignore[reportCallIssue]
        elif prank_name in ["send_fake_notifications", "Speech"]:
            prank_func(ip)
        else:
            prank_func(ip, reset=reset)  # pyright: ignore[reportCallIssue]

        print(f"{prank_name} executed on {ip}.")


scanner = SSHScanner(user="spravce", ssh_timeout=5)
scanner.run()
joke = Jokes("spravce")
joke.run()
