import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override


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

    def get_user_option(self, number_of_options: int) -> int:
        while True:
            try:
                user_choice: int = int(input("> "))
                if 1 <= user_choice <= number_of_options:
                    return user_choice
                else:
                    raise ValueError
            except ValueError:
                print("Invalid option")

    @override
    def setup(self) -> None:
        # NOTE: spd-say -o espeak-ng -l en-us -r -10 -p 5 -R 10 -y Storm -P important -w "Hello, this is a test of my voice."
        # NOTE: setup will call each function that doing some setup thing
        while True:
            self.show_options()
            user_choice: int = self.get_user_option(7)
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
        executor(ip, f"spd-say {''.join(self.options)} '{self.message}'")

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
