from datetime import time
import time  # Ensure the time module is used for timing
import threading
from tqdm import tqdm
import socket
import struct
import ANSI_colors as ac
from SeverSide import UDP_PAYLOAD_SIZE, TCP_PAYLOAD_SIZE

UDP_TIMEOUT = 1
TCP_TIMEOUT = 10
BROADCAST_PORT = 8082
MAGIC_COOKIE=0xabcddcba
MESSAGE_TYPE=0x3
PAYLOAD_FORMAT = "!I B Q Q"
PAYLOAD_HEADER_SIZE = 21

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

def SpeedTest(file_size, tcp_connections, udp_connections, udp_port, tcp_port, server_address):

    print(f"{ac.GREEN}Starting speed test...{ac.RESET}")
    if tcp_connections > 0:
        print(f"{ac.CYAN}Testing TCP Download...{ac.RESET}")
        for i in range(tcp_connections):
            print(f"{ac.YELLOW}Starting TCP connection {i+1}...{ac.RESET}")
            threading.Thread(target=TCP_download, args=(file_size, tcp_port, server_address[0])).start()
    if udp_connections > 0:
        print(f"{ac.CYAN}Testing UDP Download...{ac.RESET}")
        for i in range(udp_connections):
            print(f"{ac.YELLOW}Starting UDP connection {i+1}...{ac.RESET}")
            threading.Thread(target=UDP_speedtest, args=(file_size, udp_port, server_address[0])).start()

    print(f"{ac.GREEN}Speed test initiated. Monitor the results above.{ac.RESET}")


def TCP_download(file_size, tcp_port, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client_socket:
        tcp_client_socket.settimeout(TCP_TIMEOUT)  # Set connection timeout
        try:
            print("Connecting to server...")
            tcp_client_socket.connect((server_address, tcp_port))
            print("Connected to server. Starting download...")
            # Send the initial request message
            tcp_client_socket.send(f"{file_size}\n".encode())# send the data needed followed \n
            start_time = time.time()
            # Receive data in chunks
            received_data = bytearray()
            while len(received_data) < file_size:
                chunk = tcp_client_socket.recv(min(4096, file_size - len(received_data)))
                if not chunk:
                    break
                received_data.extend(chunk)
            end_time = time.time()
            print(f"Download completed. Data size: {len(received_data)} bytes, Time take {end_time-start_time}")
        except socket.timeout:
            print("Timeout occurred while waiting for the server response.")
        except Exception as e:
            print(f"Error during TCP download: {e}")


def UDP_speedtest(file_size, udp_port, server_address):
    message = build_request_message(file_size)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client_socket:
        udp_client_socket.settimeout(UDP_TIMEOUT)
        start_time = time.time()
        udp_client_socket.sendto(message, (server_address, udp_port))
        received_segments = {}
        total_segments = None
        try:
            while True:
                response = udp_client_socket.recv(UDP_PAYLOAD_SIZE)
                parsed_message = parse_payload_message(response)
                if parsed_message is None:
                    continue
                current_total_segments, current_segment, payload_data = parsed_message
                # Set total segments if this is the first valid message
                if total_segments is None:
                    total_segments = current_total_segments
                # Store unique segments
                if current_segment not in received_segments:
                    received_segments[current_segment] = payload_data
                    print(f"Received Segment {current_segment}/{total_segments}")
                # Stop if all segments are received
                if len(received_segments) == total_segments:
                    break
        except socket.timeout:
            print("No response received within the timeout period.")
        except Exception as e:
            print(f"Error during UDP reception: {e}")
        # Calculate transfer metrics after successful reception
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_received_bytes = sum(len(segment) for segment in received_segments.values())
        speed = total_received_bytes / elapsed_time
        print(f"Total Segments Received: {len(received_segments)}/{total_segments}")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"Transfer Speed: {speed / 1024:.2f} KB/s")

def build_request_message(file_size):
    message = struct.pack(
        '!I B Q',
        MAGIC_COOKIE,
        MESSAGE_TYPE,
        file_size
    )
    return message

def parse_payload_message(message):
    try:

        magic_cookie, message_type, total_segments, current_segment = struct.unpack(PAYLOAD_FORMAT, message[:PAYLOAD_HEADER_SIZE])
        payload_data = message[PAYLOAD_HEADER_SIZE:]
        print("before parse if")
        if magic_cookie != MAGIC_COOKIE or message_type != 0x4:
            print("Invalid message header")
            return None
        print("after parse if")
        return total_segments, current_segment, payload_data

    except struct.error as e:
        print(f"Error unpacking payload message: {e}")


def main():
    # Step 1: Get user input for the file size and number of connections
    file_size, tcp_connections, udp_connections = startup()

    # Step 2: Discover server using broadcast
    udp_port, tcp_port, server_address = server_lookup()

    print(f"{ac.GREEN}Server found!{ac.RESET}")
    print(f"UDP Port: {udp_port}, TCP Port: {tcp_port}, Server Address: {server_address[0]}")

    # Step 3: Start speed test
    SpeedTest(file_size, tcp_connections, udp_connections, udp_port, tcp_port, server_address)


if __name__ == "__main__":
    main()