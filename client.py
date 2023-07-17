import socket
import tkinter as tk
from tkinter import messagebox

def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = server_entry.get()
    port = port_entry.get()

    try:
        client_socket.connect((server_address, int(port)))
        status_label.config(text="Connected to server.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to server: {e}")
        status_label.config(text="Failed to connect to server.")

def send_message():
    message = message_entry.get()
    try:
        client_socket.sendall(message.encode())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send message: {e}")
        status_label.config(text="Failed to send message.")

# GUI setup
client_window = tk.Tk()
client_window.title("Client")

server_label = tk.Label(client_window, text="Server IP:")
server_label.pack()

server_entry = tk.Entry(client_window, width=20)
server_entry.pack()

port_label = tk.Label(client_window, text="Port:")
port_label.pack()

port_entry = tk.Entry(client_window, width=20)
port_entry.pack()

connect_button = tk.Button(client_window, text="Connect", command=connect_to_server)
connect_button.pack(pady=10)

status_label = tk.Label(client_window, text="Not connected to server.")
status_label.pack()

message_label = tk.Label(client_window, text="Message:")
message_label.pack()

message_entry = tk.Entry(client_window, width=30)
message_entry.pack()

send_button = tk.Button(client_window, text="Send", command=send_message)
send_button.pack(pady=10)

client_window.mainloop()
