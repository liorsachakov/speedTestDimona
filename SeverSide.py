import struct
from socket import *

import threading
import time


MAGIC_COOKIE=0xabcddcba
MESSAGE_TYPE=0x2
BROADCAST_PORT=8082


def build_offer_message_C2S(udp_port, tcp_port):

    # pack the message into bytes
    message = struct.pack(
        "!I B H H",
        MAGIC_COOKIE,
        MESSAGE_TYPE,
        udp_port,
        tcp_port
    )
    """Broadcast the offer message to all clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_address = ('<broadcast>', BROADCAST_PORT)
    while True:
        server_socket.sendto(message, broadcast_address)
        time.sleep(1)

udp_socket = socket(AF_INET, SOCK_DGRAM)
tcp_socket = socket(AF_INET, SOCK_STREAM)

