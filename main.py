import subprocess

def ssh_connect(ip: str):
    s = subprocess.Popen(
        ["ssh", ip],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    inputs = [
        "yes\n", "spravce\n"
    ]
    for i in inputs:
        s.stdin.write(i)
        s.stdin.flush()

    # get host name and before returning exit

def get_ips(scan_output: str) -> list[str]:
    ips: list[str] = []

    for line in scan_output.splitlines():
        if "Ports: 22/open" in line:
            ips.append(line.split()[1])

    return ips

def get_pcs(ips: list[str]):
    # for loop in ips and 
    # call ssh_connect 
    pass


def scan() -> str:
    network_ip = input("Input subnet ip : ")
    mask = input("enter subnet mask : ")
    return subprocess.check_output(["nmap", "-T4", "-p22", "-oG", "-" ,f"{network_ip}/{mask}"], text=True)
    

def run():
    scan_output = scan()
    ips = get_ips(scan_output)
    get_pcs(ips)
    # refractor code to OOP 

run()
