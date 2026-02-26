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
    def __init__(self) -> None:
        self.message: str = "Hello. I am inside the machine."
        self.volume: int = 0
        self.language: str = "en"
        self.language_option: str = ""

    @override
    def get_name(self) -> str:
        return "Speech"

    @override
    def can_reset(self) -> bool:
        return False

    @override
    def setup(self) -> None:
        # setup will call each function that doing some setup thing
        pass

    @override
    def run(self, executor: Callable[[str, str], None], ip: str) -> None:
        executor(ip, f"spd-say -i {self.volume} '{self.message}'")

    @override
    def reset(self, executor: Callable[[str, str], None], ip: str) -> None:
        pass

    @override
    def save(self) -> None:
        # save configuration
        pass

    def set_volume(self):
        # set the volume (intensity) of the speech (between -100 and +100, default: 0)
        while True:
            try:
                self.volume = int(input("Volume (-100 - 100): "))
            except ValueError:
                print("Bad input")
                continue

            return

    def set_msg(self):
        self.message = input("Enter custom msg: ")

    def set_language(self):
        self.language = self.get_language()
        self.language_option = f"-l {self.language}"

    def get_language(self) -> str:
        while True:
            language: str = input("language> ")
            match language:
                case lang if "en" in lang:
                    return "en"

                case lang if "cs" in lang:
                    return "cs"

                case _:
                    print("Help [en|cs]")

    def set_voice(self):
        pass
