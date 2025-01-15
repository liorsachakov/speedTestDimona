import struct

import socket

import threading
import time
from random import random

MAGIC_COOKIE=0xabcddcba
OFFER_MESSAGE_TYPE=0x2
BROADCAST_PORT=8082
UDP_PORT= 8080
TCP_PORT= 8081
MAXIMUM_CLIENTS_NUMBER=10
UDP_PAYLOAD_SIZE= 1024
TCP_PAYLOAD_SIZE= 1024
REQUEST_MESSAGE_TYPE = 0x3
PAYLOAD_MESSAGE_TYPE = 0x4

def build_offer_message_s2c(udp_port, tcp_port):
    # pack the message into bytes
    message = struct.pack(
        "!I B H H",
        MAGIC_COOKIE,
        OFFER_MESSAGE_TYPE,
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
        server_socket.bind(("", TCP_PORT))
        server_socket.listen(1)
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                threading.Thread(target=handle_tcp_requests,args=(client_socket, client_address)).start()
            except Exception as e:
                print(e)

def handle_tcp_requests(client_socket, client_address):
    try:
        message = client_socket.recv(1024).decode().strip()  # Decode and remove the newline

        if not message:
            print("Invalid message, no file size received." )
            return
        try:
            received_file_size = int(message)
            print(f"Received file size: {received_file_size}")
        except ValueError:
            print("Invalid file size received.")
            return
        chunk_size = 1000
        bytes_sent = 0
        print("Sending data...")
        while bytes_sent < received_file_size:
            remaining_data_size = received_file_size - bytes_sent
            chunk = b'\x00' * min(chunk_size, remaining_data_size)  # Generate the next chunk
            client_socket.sendall(chunk)
            bytes_sent += len(chunk)  # Track the amount of data sent
        print("Data sent successfully.")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        client_socket.close()




def open_udp_server(ip_address):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_socket:
        UDP_socket.bind((ip_address, UDP_PORT))
        while True:
            try:
                message, client_address = UDP_socket.recvfrom(1024)
                threading.Thread(target=handle_udp_requests,args=(message, client_address)).start()
            except Exception as e:
                print(e)
def handle_udp_requests(message, client_address):
    format_string = '!I B Q'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # unpack the received message
            received_magic_cookie, received_message_type, received_file_size = struct.unpack(format_string, message)
            #validate the unpacked values
            if received_magic_cookie != MAGIC_COOKIE or received_message_type != REQUEST_MESSAGE_TYPE:
                print("Invalid message header")
                return
            # process the valid request
            segment_size = UDP_PAYLOAD_SIZE - 21
            total_segments = (received_file_size + segment_size - 1) // segment_size
            bytes_sent = 0
            for segment_num in range(total_segments):
                remaining = received_file_size - bytes_sent
                current_size = min(segment_size, remaining)
                payload = b'\x00'* current_size
                packet = struct.pack('!IbQQ', MAGIC_COOKIE, PAYLOAD_MESSAGE_TYPE, total_segments, segment_num) + payload
                udp_socket.sendto(packet, client_address)
                bytes_sent += current_size
    #add further processing here (e.g., sending a response back to the client)
    except struct.error as e:
        print(e)






def main():
    """Main entry point to start TCP and UDP servers."""
    ip_address = ""  # Example IP address, replace as needed

    print("Server started, listening on IP address " + ip_address)
    tcp_thread = threading.Thread(target=open_tcp_server, args=(ip_address,))
    udp_thread = threading.Thread(target=open_udp_server, args=(ip_address,))
    broadcast_thread = threading.Thread(target=broadcast_message_s2c)

    tcp_thread.start()
    udp_thread.start()
    broadcast_thread.start()

    # Join the threads to wait for their completion
    tcp_thread.join()
    udp_thread.join()
    broadcast_thread.join()


if __name__ == "__main__":
    main()

