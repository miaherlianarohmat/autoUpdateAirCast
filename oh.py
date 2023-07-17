import socket

def send_command(client_socket, command):
    client_socket.send(command.encode())

def receive_response(client_socket):
    response = client_socket.recv(1024).decode()
    return response

def handle_client(client_socket):
    while True:
        command = input("Enter command: ")

        if command == "find_aircast_directory":
            send_command(client_socket, command)
            response = receive_response(client_socket)
            print("Aircast Docker directory on client:", response)

        # Tambahkan perintah lain sesuai kebutuhan

# Inisialisasi server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.68.102', 8506)  # Ganti dengan alamat dan port server yang sesuai
server_socket.bind(server_address)
server_socket.listen(1)

print("Server is running...")

while True:
    client_socket, client_address = server_socket.accept()
    print("Connected to client:", client_address)

    handle_client(client_socket)

    client_socket.close()
