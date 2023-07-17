import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import string
import time
import socket
from discord_webhook import DiscordWebhook

#server on
def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.100.19', 8500)  # Replace with your desired server IP address and port number

    try:
        server_socket.bind(server_address)
        server_socket.listen(1)
        status_label.config(text="Server is listening...")
        accept_connections()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start server: {e}")
        status_label.config(text="Server failed to start.")
        server_socket.close()

def accept_connections():
    while True:
        connection, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(connection, client_address)).start()

def handle_client(connection, client_address):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            received_text = data.decode()

            # Cek apakah permintaan adalah untuk mencari direktori aircast-docker
            if received_text == "request_directory":
                aircast_directory = find_aircast_docker_directory()
                connection.sendall(aircast_directory.encode())
            else:
                log_text.config(state=tk.NORMAL)
                log_text.insert(tk.END, f"Received from {client_address}: {received_text}\n")
                log_text.config(state=tk.DISABLED)
                
    except Exception as e:
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"Error from {client_address}: {e}\n")
        log_text.config(state=tk.DISABLED)
    finally:
        connection.close()

def start_server_thread():
    threading.Thread(target=start_server).start()

# Auto Update
# Mendapatkan path dari file program utama
program_dir = os.path.dirname(os.path.abspath(__file__))

def get_recipient_name():
    try:
        file_path = os.path.join(program_dir, 'recipient.txt')
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def run_ecr_login():
    try:
        ecr_command = ['aws', 'ecr', 'get-login-password', '--region', 'ap-southeast-1']
        ecr_password = subprocess.check_output(ecr_command).decode('utf-8').strip()

        docker_command = ['docker', 'login', '--username', 'AWS', '--password-stdin', '534332024917.dkr.ecr.ap-southeast-1.amazonaws.com']
        subprocess.run(docker_command, input=ecr_password.encode('utf-8'), creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        error_message = "Error: Gagal Connect ke AWS ECR. Kode keluaran: {}\n{}".format(e.returncode, e.output.decode('utf-8'))
        show_status(error_message)

def run_docker_compose_down(compose_dir):
    try:
        command = ['docker-compose', 'down']
        subprocess.run(command, cwd=compose_dir, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        error_message = "Error: Gagal menjalankan Update Aircast. Kode keluaran: {}\n{}".format(e.returncode, e.output.decode('utf-8'))
        show_status(error_message)

def run_docker_compose_up(compose_dir):
    try:
        command = ['docker-compose', 'up', '-d']
        subprocess.run(command, cwd=compose_dir, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        show_completion_message()
    except subprocess.CalledProcessError as e:
        error_message = "Error: Gagal menjalankan Update Aircast. Kode keluaran: {}\n{}".format(e.returncode, e.output.decode('utf-8'))
        show_status(error_message)

def send_discord_notification():
    webhook_url = 'https://discord.com/api/webhooks/1108999294276620318/UPbYfYnnOjepMrzRDn_Wdr0F9U4WNfHXMa_yFhiHcY-vupk_F_lqlr6ZbJKAK08X3Pub'  # Replace with your actual webhook URL
    content = f"{recipient_name} Proses Update Aircast selesai."
    webhook = DiscordWebhook(url=webhook_url, content=content)
    webhook.execute()

def show_completion_message():
    show_status("Proses selesai.")
    messagebox.showinfo("Proses Selesai", "Proses Update Aircast selesai.")
    send_discord_notification()

def show_status(text):
    status_label.config(text=text)

def hide_status():
    status_label.config(text="")

def check_docker_running():
    try:
        command = ['docker', 'version']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except OSError:
        return False

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

def update_docker_status():
    while True:
        if check_docker_running():
            docker_status_label.config(text="Docker: Running", fg="green")
        else:
            docker_status_label.config(text="Docker: Stopped", fg="red")
        time.sleep(1)  # Perbarui status setiap 1 detik

def run_commands():
    compose_dir = compose_dir_entry.get()

    if not check_docker_running():
        messagebox.showwarning("Peringatan", "Docker tidak berjalan. Mohon pastikan Docker telah diinstal dan berjalan.")
        return

    if not compose_dir:
        messagebox.showwarning("Peringatan", "Silakan isi Directory Aircast.")
        return

    global recipient_name
    recipient_name = get_recipient_name()

    if not recipient_name:
        messagebox.showwarning("Peringatan", "File recipient.txt tidak ditemukan.")
        return

    # Menjalankan fungsi-fungsi di thread terpisah
    ecr_thread = threading.Thread(target=run_ecr_login)
    compose_down_thread = threading.Thread(target=run_docker_compose_down, args=(compose_dir,))
    compose_up_thread = threading.Thread(target=run_docker_compose_up, args=(compose_dir,))

    show_status("Proses sedang berjalan...")
    ecr_thread.start()
    compose_down_thread.start()
    compose_down_thread.join()
    compose_up_thread.start()

def window():
    server_window.destroy()
    
# GUI setup server
server_window = tk.Tk()
server_window.title("Server")

start_button = tk.Button(server_window, text="Start Server", command=start_server_thread)
start_button.pack(pady=10)

status_label = tk.Label(server_window, text="Server is not running.")
status_label.pack()

log_text = tk.Text(server_window, width=50, height=15, state=tk.DISABLED)
log_text.pack(pady=10)

# Button Next
next_button = tk.Button(server_window, text="Next", command=window)
next_button.pack(pady=10)

server_window.mainloop()

# Auto Up
# Buat jendela utama
window = tk.Tk()
window.title("Update Aircast Web")

# Buat frame utama
main_frame = tk.Frame(window, padx=20, pady=20)
main_frame.pack()

# Buat label dan input untuk compose_dir
compose_dir_label = tk.Label(main_frame, text="Directory Aircast:")
compose_dir_label.pack()

compose_dir_entry = tk.Entry(main_frame, width=50)
compose_dir_entry.pack(pady=5)

# Buat label untuk status Docker
docker_status_label = tk.Label(main_frame, text="Docker: ", fg="black")
docker_status_label.pack()

# Buat label untuk status
status_label = tk.Label(main_frame, text="", width=30)
status_label.pack(pady=5)

# Set nilai default untuk compose_dir_entry dengan hasil pencarian direktori
default_directory = find_aircast_docker_directory()
compose_dir_entry.insert(tk.END, default_directory)

# Menjalankan fungsi update_docker_status di thread terpisah
docker_status_thread = threading.Thread(target=update_docker_status)
docker_status_thread.daemon = True
docker_status_thread.start()

# Buat tombol "Run Update"
run_button = tk.Button(main_frame, text="Run Update", command=run_commands)
run_button.pack(pady=10)

# Jalankan jendela GUI
window.mainloop()

#ini baru bisa nyambungin ke jaringan yang sama file client ada di client.py
#udah bisa ngirim pesan pemberitahuan lewat client
#buat nyari direktori ada di file oh.py dan oh-client.py
#bingungnya ini mau dijadiin exe atau