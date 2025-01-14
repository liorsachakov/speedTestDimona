from socket import *
from struct import *
import threading

import socket
import struct
import ANSI_colors as ac
BROADCAST_PORT = 8082
MAGIC_COOKIE=0xabcddcba
MESSAGE_TYPE=0x2
def startup():
    print(f"{ac.CYAN}Hey, please provide me the following parameters{ac.RESET}")
    while True:
        try:
            file_size = int(input(f"{ac.BOLD}{ac.YELLOW}Enter the file size in bytes: {ac.RESET}"))
            if file_size > 0:
                break
            else:
                print(f"{ac.RED}Please enter a positive number.{ac.RESET}")
        except ValueError:
            print(f"{ac.RED}Invalid input. Please enter an integer.{ac.RESET}")
    while True:
        try:
            tcp_connections = int(input(f"{ac.BOLD}{ac.YELLOW}Enter the number of TCP connections: {ac.RESET}"))
            if tcp_connections >= 0:
                break
            else:
                print(f"{ac.RED}Please enter a positive number.{ac.RESET}")
        except ValueError:
            print(f"{ac.RED}Invalid input. Please enter an integer.{ac.RESET}")
    while True:
        try:
            udp_connections = int(input(f"{ac.BOLD}{ac.YELLOW}Enter the number of UDP connections: {ac.RESET}"))
            if udp_connections >= 0:
                break
            else:
                print(f"{ac.RED}Please enter a positive number.{ac.RESET}")
        except ValueError:
            print(f"{ac.RED}Invalid input. Please enter an integer.{ac.RESET}")

    return file_size, tcp_connections, udp_connections


def server_lookup():
    print("● Client started, listening for offer requests...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client_socket.bind(("", BROADCAST_PORT))
            while True:
                message, server_address = client_socket.recvfrom(1024)
                try:
                    magic_cookie_rcv, message_type_rcv, udp_port, tcp_port = struct.unpack("!I B H H", message)
                    if magic_cookie_rcv == MAGIC_COOKIE or message_type_rcv == MESSAGE_TYPE:
                        return  udp_port, tcp_port,server_address
                except struct.error as e:
                    print(f"{ac.RED}Invalid offer message.{ac.RESET}")
    except Exception as e:
        print(f"{ac.RED}Error occurred.{ac.RESET}")

def SpeedTest(file_size, tcp_connections, udp_connections,udp_port, tcp_port,server_address):


def UDP_speedtest(file_size,udp_port,server_address):
    message = build_request_message(file_size)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(message, (server_address, udp_port))



def build_request_message(file_size):
    message = struct.pack(
        '!I B Q',
        MAGIC_COOKIE,
        MESSAGE_TYPE,
        file_size
    )
    return message

