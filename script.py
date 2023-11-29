import asyncio
import concurrent.futures
import json
import random
import socket
from colorama import Fore, Style

def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print("Le fichier config.json est introuvable.")
        exit(1)

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def is_port_open(ip, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    except Exception as e:
        return False
    finally:
        sock.close()

def check_ports(ip, port, timeout):
    try:
        if is_port_open(ip, port, timeout):
            print(f"{Fore.GREEN}{ip}:{port}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}{ip}:{port}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}{ip}:{port} - {e}{Style.RESET_ALL}")
        return False

async def generate_and_check_ips(num_threads, timeout_seconds, port, output_file="live.txt", num_ips=1000):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        while True:
            ips = [generate_random_ip() for _ in range(num_ips)]
            tasks = [loop.run_in_executor(executor, check_ports, ip, port, timeout_seconds) for ip in ips]
            results = await asyncio.gather(*tasks)
            if any(results):
                with open(output_file, "a") as live_file:
                    for ip, result in zip(ips, results):
                        if result:
                            live_file.write(f"{ip}:{port}\n")

if __name__ == "__main__":
    config = load_config()
    num_threads = config["num_threads"]
    timeout_seconds = config["timeout_seconds"]
    port = config["port"]

    try:
        asyncio.run(generate_and_check_ips(num_threads, timeout_seconds, port))
    except KeyboardInterrupt:
        pass
