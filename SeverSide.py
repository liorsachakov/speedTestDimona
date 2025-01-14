import struct
from socket import *

import threading
import time


MAGIC_COOKIE=0xabcddcba
MESSAGE_TYPE=0x2
BROADCAST_PORT=8082
UDP_PORT=8080
TCP_PORT=8081
MAXIMUM_CLIENTS_NUMBER=10
UDP_PAYLOAD_SIZE=1024

def build_offer_message_s2c(udp_port, tcp_port):
    # pack the message into bytes
    message = struct.pack(
        "!I B H H",
        MAGIC_COOKIE,
        MESSAGE_TYPE,
        udp_port,
        tcp_port
    )
    return message

def broadcast_message_s2c():
    """Broadcast the offer message to all clients."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception as e:
        print(e)
    broadcast_address = ('<broadcast>', BROADCAST_PORT)
    while True:
        try:
            server_socket.sendto(build_offer_message_s2c(UDP_PORT, TCP_PORT), broadcast_address)
        except Exception as e:
            print(e)
        time.sleep(1)
def open_tcp_server(ip_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip_address, TCP_PORT))
        server_socket.listen(MAXIMUM_CLIENTS_NUMBER)
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                threading.Thread(target=handle_tcp_requests,args=(client_socket, client_address)).start()
            except Exception as e:
                print(e)

def open_udp_server(ip_address):
    with socket(AF_INET, SOCK_DGRAM) as UDP_socket:
        UDP_socket.bind((ip_address, UDP_PORT))
        UDP_socket.listen(MAXIMUM_CLIENTS_NUMBER)
        while True:
            try:
                message, client_address = udp_socket.recvfrom(1024)
                threading.Thread(target=handle_udp_requests,args=(message, client_address)).start()
            except Exception as e:
                print(e)
def handle_udp_requests(message, client_address):
    format_string = '!I B Q'
    try:
        # unpack the received message
        received_magic_cookie, received_message_type, received_file_size = struct.unpack(format_string, message)
        #validate the unpacked values
        if received_magic_cookie != MAGIC_COOKIE or received_message_type != 0x3:
            return
        # process the valid request

    #add further processing here (e.g., sending a response back to the client)
    except struct.error as e:
        print(e)


def handle_tcp_requests(socket, client_address):

def build_payload_message(payload_size,file_size,):
    segments_number=(file_size+payload_size-1)//payload_size
    for seg in range(segments_number):



udp_socket = socket(AF_INET, SOCK_DGRAM)
tcp_socket = socket(AF_INET, SOCK_STREAM)

