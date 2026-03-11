#!/usr/bin/env python3
from ssh_connection import SSHConnection
from scanner import pc_to_ip_mapping, validate_ipv4
from pranks import * 


class Jokes:
    """
    GNOME pranks over SSH.
    Each prank has apply() and reset() methods.
    """

    def __init__(self, user: str) -> None:
        self.user: str = user
        self.target_pc: str = ""
        self.prank_index: int = -1
        self.ssh_connection: SSHConnection = SSHConnection(user=user)
        self.speech: Speech = Speech()
        self.dvd_tray: DVDTray = DVDTray()
        self.rotate_screen: RotateScreen = RotateScreen()
        self.cursor_theme: CursorTheme = CursorTheme()
        self.min_window_size: MinimumWindowSize = MinimumWindowSize()
        self.mouse: Mouse = Mouse()
        self.wallpaper_prank: Wallpaper = Wallpaper(self.ssh_connection)
        self.delay_commands: DelayCommands = DelayCommands()

        self.menu = [
            ("Invert mouse buttons", self.invert_mouse_buttons),
            ("send_fake_notifications", self.send_fake_notifications),
            ("Cursor size", self.cursor_size),
            ("Random cursor size", self.random_cursor_size),
            ("Animations / primary paste", self.animations),
            ("Cursor blink", self.cursor_blink),
            ("Natural scroll", self.natural_scroll),
            ("Keyboard delay", self.keyboard_delay),
            ("Speech", self.speech),
            ("DVD Tray", self.dvd_tray),
            ("Rotate Screen", self.rotate_screen),
            ("Cursor Theme", self.cursor_theme),
            ("Minimum Window Size", self.min_window_size),
            ("Mouse", self.mouse),
            ("Wallpaper", self.wallpaper_prank),
            ("Delay Commands", self.delay_commands),
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

    def get_target_pc(self) -> None:
        global pc_to_ip_mapping
        while True:
            self.target_pc = input("Write pc hostname : ")
            if self.target_pc in pc_to_ip_mapping:
                return
            print(f"Host '{self.target_pc}' not found. Available: {list(pc_to_ip_mapping.keys())}")

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
    
    def is_target_set(self) -> bool:
        return False if self.target_pc == "" else True

    def is_prank_set(self) -> bool:
        return False if self.prank_index == -1 else True 

    # NOTE:
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
        # TODO:
        # here and in the  functions above can be used like
        # cmd and just reset/set and value for it, so
        # it dont need to be two long strings, more clean
        cmd: str = (
            "gsettings reset org.gnome.desktop.peripherals.keyboard delay"
            if reset
            else "gsettings set org.gnome.desktop.peripherals.keyboard delay 1000"
        )
        self.execute_remote(ip, cmd)


    # NOTE:
    # NOTE:
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
    
    # NOTE:
    # ****************************************************************************************************
    #                   Start of the program
    # ****************************************************************************************************
    def run(self) -> None:
        global pc_to_ip_mapping
        
        if self.is_target_set():
            return print("Target no set")
        
        if self.is_prank_set():
            return print("Prank not set")

        
        ip: str = pc_to_ip_mapping[self.target_pc]

        prank_name, prank_func = self.menu[self.prank_index]

        reset: bool = False
        if prank_name not in [
            "send_fake_notifications",
            "Speech",
            "Random cursor size",
            "DVD Tray",
            "Rotate Screen",
            "Cursor Theme",
            "Minimum Window Size",
            "Mouse",
            "Wallpaper",
            "App Icons",
            "Delay Commands",
        ]:
            resp: str = (
                input("Do you want to reset instead of apply? (y/N): ").strip().lower()
            )
            reset = resp == "y"


        if isinstance(prank_func, Prank):
            if not reset:
                prank_func.setup()
            if reset and prank_func.can_reset():
                prank_func.reset(self.execute_remote, ip)
            else:
                prank_func.run(self.execute_remote, ip)
            print(f"{prank_name} executed on {ip}.")
            return
        elif prank_name == "send_fake_notifications":
            prank_func(ip)
        else:
            prank_func(ip, reset=reset)

        print(f"{prank_name} executed on {ip}.")



