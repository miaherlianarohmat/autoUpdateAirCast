import socket
import os
import string

def send_response(client_socket, response):
    client_socket.send(response.encode())

def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = letter + ":\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def find_aircast_docker_directory():
    drives = get_available_drives()
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if 'aircast-docker' in dirs:
                return os.path.join(root, 'aircast-docker')
    return ""

def handle_server_commands(server_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    while True:
        command = client_socket.recv(1024).decode()

        if command == "find_aircast_directory":
            directory = find_aircast_docker_directory()
            send_response(client_socket, directory)

        # Tambahkan perintah lain sesuai kebutuhan

    client_socket.close()

# Inisialisasi alamat server
server_address = ('192.168.68.102', 8506)  # Ganti dengan alamat dan port server yang sesuai
handle_server_commands(server_address)