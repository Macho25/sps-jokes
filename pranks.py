import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override
from ssh_connection import *
def get_user_option(number_of_options: int) -> int:
    while True:
        try:
            user_choice: int = int(input("> "))
            if 1 <= user_choice <= number_of_options:
                return user_choice
            else:
                raise ValueError
        except ValueError:
            print("Invalid option")

class Prank(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def can_reset(self) -> bool:
        pass

    @abstractmethod
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        pass

    @abstractmethod
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        pass

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass


class Speech(Prank):
    # options: -i = volume, -l = language, -t = voice_type
    CONFIG_FILE: str = "speech_config.json"

    def __init__(self) -> None:
        self.message: str = "Hello. I am inside the machine."
        self.volume: int = 0
        self.language: str = "en"
        self.voice_type: str = ""

        # Default spd-say options for good sounding voice
        self.options: list[str] = [
            "-o espeak-ng",
            "-r -10",
            "-p 5",
            "-R 10",
            "-y Storm",
            "-P important",
        ]

        self.voice_types: list[str] = [
            "male1",
            "male2",
            "male3",
            "female1",
            "female2",
            "female3",
            "child_male",
            "child_female",
        ]

        self.languages: list[str] = ["en", "cs"]

    def _reset_to_defaults(self) -> None:
        self.message = "Hello. I am inside the machine."
        self.volume = 0
        self.language = "en"
        self.voice_type = ""
        # Default spd-say options for good sounding voice
        self.options = [
            "-o espeak-ng",
            "-r -10",
            "-p 5",
            "-R 10",
            "-y Storm",
            "-P important",
        ]

    @override
    def get_name(self) -> str:
        return "Speech"

    @override
    def can_reset(self) -> bool:
        return False

    def show_options(self) -> None:
        print("=== Speech prank setup ===")
        print("1. Message")
        print("2. Volume")
        print("3. Language")
        print("4. Voice type")
        print("5. Show config")
        print("6. Reset")
        print("7. Save and exit")


    @override
    def setup(self) -> None:
        # NOTE: spd-say -o espeak-ng -l en-us -r -10 -p 5 -R 10 -y Storm -P important -w "Hello, this is a test of my voice."
        # NOTE: setup will call each function that doing some setup thing
        while True:
            self.show_options()
            user_choice: int = get_user_option(7)
            match user_choice:
                case 1:
                    self.set_message()
                case 2:
                    self.set_volume()
                case 3:
                    self.set_language()
                case 4:
                    self.set_voice()
                case 5:
                    self.show_config()
                case 6:
                    self.reset_config()
                case 7:
                    self.save()
                    return
                case _:
                    print("Invalid option")

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        print(f"{' '.join(self.options)}")
        executor(ip, f"spd-say {' '.join(self.options)} '{self.message}'")

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        # NOTE: reset() will not be implemented = doesnt need
        pass

    @override
    def save(self) -> None:
        config = {
            "message": self.message,
            "volume": self.volume,
            "language": self.language,
            "voice_type": self.voice_type,
        }
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"Config saved to {self.CONFIG_FILE}")

    def reset_config(self) -> None:
        self._reset_to_defaults()
        print("Config reset to defaults")

    def show_config(self) -> None:
        print("=== Current Config ===")
        print(f"Message: {self.message}")
        print(f"Volume: {self.volume}")
        print(f"Language: {self.language}")
        print(f"Voice type: {self.voice_type or 'default'}")

    def set_volume(self) -> None:
        self.volume = self.get_volume()
        self.options.append(f"-i {self.volume} ")

    def get_volume(self) -> int:
        # set the volume (intensity) of the speech (between -100 and +100, default: 0)
        while True:
            try:
                volume = int(input("Volume (-100 to 100): "))
                if -100 <= volume <= 100:
                    return volume
                else:
                    print("Value must be between -100 and 100")
            except ValueError:
                print("Invalid input. Enter a number.")

    def set_message(self) -> None:
        self.message = input("Enter custom msg: ")

    def set_language(self) -> None:
        self.language = self.get_language()
        self.options.append(f"-l {self.language} ")

    def get_language(self) -> str:
        while True:
            print("=== Languages ===")
            for i, lang in enumerate(self.languages, 1):
                print(f"{i}. {lang}")
            try:
                choice = int(input("> "))
                if 1 <= choice <= len(self.languages):
                    return self.languages[choice - 1]
            except ValueError:
                pass
            print("Invalid option")

    def set_voice(self) -> None:
        self.voice_type = self.get_voice()
        self.options.append(f"-t {self.voice_type} ")

    def get_voice(self) -> str:
        while True:
            print("=== Voice Types ===")
            for i, voice in enumerate(self.voice_types, 1):
                print(f"{i}. {voice}")
            try:
                choice = int(input("> "))
                if 1 <= choice <= len(self.voice_types):
                    return self.voice_types[choice - 1]
            except ValueError:
                pass
            print("Invalid option")
# NOTE:
# ******************************************
#      DVD - for opening a closing dvd tray
# ******************************************
class DVDTray(Prank):
    def __init__(self) -> None:
        self.action: str = "open" 
        self.states: list[str] = ["open", "close"]
    @override
    def get_name(self) -> str:
        return "DVD Tray"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== DVD Tray prank ===")
        print("1. Open tray")
        print("2. Close tray")
        choice: int = get_user_option(2)
        self.action = self.states[choice] 

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        cmd = "eject" if self.action == "open" else "eject -t"
        executor(ip, cmd)

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        cmd = "eject -t" if self.action == "open" else "eject"
        executor(ip, cmd)
# NOTE:
# ******************************************
#    Rotate Sceen
# ******************************************
class RotateScreen(Prank):
    def __init__(self) -> None:
        self.rotation: str = "left"

    @override
    def get_name(self) -> str:
        return "Rotate Screen"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== Rotate Screen prank ===")
        print("1. Rotate left")
        print("2. Rotate right")
        print("3. Inverted")
        choice = input("> ")
        rotations = ["left", "right", "inverted"]
        self.rotation = rotations[int(choice) - 1] if choice in "123" else "left"

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        cmd = f"xrandr --output DP-1 --rotate {self.rotation}"
        executor(ip, cmd)

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, "xrandr --output DP-1 --rotate normal")


class CursorTheme(Prank):
    def __init__(self) -> None:
        self.theme: str = "Adwaita"

    @override
    def get_name(self) -> str:
        return "Cursor Theme"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== Cursor Theme prank ===")
        self.theme = input("Enter cursor theme name: ") or "Adwaita"

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, f'gsettings set org.gnome.desktop.interface cursor-theme "{self.theme}"')

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, "gsettings reset org.gnome.desktop.interface cursor-theme")


class MinimumWindowSize(Prank):
    def __init__(self) -> None:
        self.width: int = 800
        self.height: int = 600

    @override
    def get_name(self) -> str:
        return "Minimum Window Size"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== Minimum Window Size prank ===")
        self.width = int(input("Width (default 800): ") or 800)
        self.height = int(input("Height (default 600): ") or 600)

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, f"gsettings set org.gnome.mutter minimum-window-width {self.width}")
        executor(ip, f"gsettings set org.gnome.mutter minimum-window-height {self.height}")

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, "gsettings reset org.gnome.mutter minimum-window-width")
        executor(ip, "gsettings reset org.gnome.mutter minimum-window-height")


class DelayCommands(Prank):
    def __init__(self) -> None:
        self.delay: int = 1
        self.aliases: dict[str, str] = {}

    @override
    def get_name(self) -> str:
        return "Delay Commands"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== Delay Commands prank ===")
        self.delay = int(input("Delay in seconds: ") or 1)
        print("Add aliases (empty to finish):")
        while True:
            alias = input("Alias name (e.g., ls): ").strip()
            if not alias:
                break
            cmd = input(f"Command for {alias}: ").strip()
            self.aliases[alias] = f"sleep {self.delay}; {cmd} $@"

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        bash_aliases = "\n".join(f"alias {alias}='{cmd}'" for alias, cmd in self.aliases.items())
        executor(ip, f"echo '{bash_aliases}' >> ~/.bash_aliases")

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        for alias in self.aliases.keys():
            executor(ip, f"sed -i '/alias {alias}=/d' ~/.bash_aliases")

# TODO: make also show config as is in Speech
class Mouse(Prank):
    def __init__(self) -> None:
        self.size: int = 24
        self.theme: str = "Adwaita"
        self.speed: int = 1
        self.reversed: bool = False
        self.natural_scroll: bool = False
        self.random_size: bool = False
        self.random_interval: int = 3
        self.random_long_last: int = 10         # how long it will run

    @override
    def get_name(self) -> str:
        return "Mouse"

    @override
    def can_reset(self) -> bool:
        return True

    @override
    def setup(self) -> None:
        print("=== Mouse prank ===")
        print("1. Set size")
        print("2. Set theme")
        print("3. Set speed")
        print("4. Reverse buttons")
        print("5. Natural scroll")
        print("6. Random size (loop)")
        choice: int = get_user_option(6)
        # TODO: need to add error handling for input
        match choice:
            case 1:
                self.size = int(input("Size (24-256): ") or 24)
            case 2:
                self.theme = input("Theme: ") or "Adwaita"
            case 3:
                self.speed = int(input("Speed (1-10): ") or 1)
            case 4:
                self.reversed = True
            case 5:
                self.natural_scroll = True
            case 6:
                self.random_size = True
                self.random_interval = int(input("Interval seconds: ") or 3)
                self.random_long_last = int(input("Set how long script should run: "))

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        import random
        times: int = 0
        while True:
            if self.random_size and times <= self.random_long_last:
                size = random.randint(24, 256)
                executor(ip, f"gsettings set org.gnome.desktop.interface cursor-size {size}")
                times += 1
                import time
                time.sleep(self.random_interval)
            else:
                if self.size:
                    executor(ip, f"gsettings set org.gnome.desktop.interface cursor-size {self.size}")
                if self.theme:
                    executor(ip, f'gsettings set org.gnome.desktop.interface cursor-theme "{self.theme}"')
                if self.speed:
                    executor(ip, f"gsettings set org.gnome.desktop.peripherals.mouse speed {self.speed}")
                if self.reversed:
                    executor(ip, "gsettings set org.gnome.desktop.peripherals.mouse left-handed true")
                if self.natural_scroll:
                    executor(ip, "gsettings set org.gnome.desktop.peripherals.mouse natural-scroll true")
            break

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, "gsettings reset org.gnome.desktop.interface cursor-size")
        executor(ip, "gsettings reset org.gnome.desktop.interface cursor-theme")
        executor(ip, "gsettings reset org.gnome.desktop.peripherals.mouse speed")
        executor(ip, "gsettings reset org.gnome.desktop.peripherals.mouse left-handed")
        executor(ip, "gsettings reset org.gnome.desktop.peripherals.mouse natural-scroll")


class Wallpaper(Prank):
    def __init__(self, ssh_connection: SSHConnection) -> None:
        self.image_path: str = ""
        self.kernel_panic: bool = False
        self.ssh_connection: SSHConnection  = ssh_connection

    @override
    def get_name(self) -> str:
        return "Wallpaper"

    @override
    def can_reset(self) -> bool:
        return True

    def _validate_wallpaper_path(self) -> str:
        while True:
            wallpaper_path: str = input("Enter wallpaper path: ")
            try:
                with open(wallpaper_path, "r"):
                    pass
                return wallpaper_path
            except Exception as e:
                print(e)

    @override
    def setup(self) -> None:
        print("=== Wallpaper prank ===")
        print("1. Set wallpaper")
        print("2. Kernel panic (fake)")
        choice = get_user_option(2)
        if choice == 1:
            self.image_path = self._validate_wallpaper_path()
            self.kernel_panic = False
        else:
            self.kernel_panic = True

    @override
    def save(self) -> None:
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        if self.kernel_panic:
            executor(ip, 'gsettings set org.gnome.desktop.background picture-uri "file:///usr/share/gnome-shell/theme/gnome-shell-logo.png"')
        elif self.image_path and self.ssh_connection:
            self.ssh_connection.connect(ip)
            remote_path = "/tmp/wallpaper.jpg"
            self.ssh_connection.scp(self.image_path, remote_path)
            set_cmd = f'gsettings set org.gnome.desktop.background picture-uri "file://{remote_path}"'
            self.ssh_connection.execute_quiet(set_cmd)

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, "gsettings reset org.gnome.desktop.background picture-uri")
        executor(ip, "gsettings reset org.gnome.desktop.background picture-uri-dark")







