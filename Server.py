# Complex Engineering Activity, File Transfer System using SOCKET programming

#    Group Members
# Ebaa Haq (2021-CE-22)
# Maham Nadeem (2021-CE-10)
# Faiza Riaz (2021_CE-20)
# Sana Israr (2021-CE-55)

# This is Server code to Send audio frames over TCP

import socket
import threading
import tkinter as tk
import wave
import pyaudio
import pickle
import struct
import tkinter.messagebox as messagebox
import os

class ServerGUI:
    def __init__(self):
        self.host_name = socket.gethostname()
        self.host_ip = '10.5.152.164'  # Set to appropriate IP address
        self.port = 9611
        self.server_socket = None
        self.client_sockets = []
        self.lock = threading.Lock()  # Adding a lock for thread-safe operations on the client_sockets list

        self.root = tk.Tk()
        self.root.title("Server")
        self.status_label = tk.Label(self.root, text="Not Connected")
        self.status_label.pack()

        self.client_count_label = tk.Label(self.root, text="Clients Connected: 0")
        self.client_count_label.pack()

        self.connect_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.connect_button.pack()

        self.send_audio_button = tk.Button(self.root, text="Send Audio File", command=self.send_audio_file, state=tk.DISABLED)
        self.send_audio_button.pack()

        self.disconnect_button = tk.Button(self.root, text="Disconnect All", command=self.disconnect_all, state=tk.DISABLED)
        self.disconnect_button.pack()

    def start_server(self):
        self.server_socket = socket.socket()
        self.server_socket.bind((self.host_ip, self.port))
        self.server_socket.listen(5)
        self.status_label.config(text="Server Listening at " + self.host_ip)
        self.connect_button.config(state=tk.DISABLED)
        self.send_audio_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.NORMAL)
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            with self.lock:
                self.client_sockets.append(client_socket)
                self.update_client_count()  # Update GUI every time a new client connects
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            messagebox.showinfo("Client Connected", f"Client connected from {addr}")

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break  # Client has disconnected
        except Exception as e:
            print(f"Error with client {client_socket}: {e}")
        finally:
            with self.lock:
                if client_socket in self.client_sockets:
                    self.client_sockets.remove(client_socket)
                    self.update_client_count()  # Update GUI when a client disconnects
            client_socket.close()

    def update_client_count(self):
        # Ensure this method is called within a locked context to maintain thread safety
        self.client_count_label.config(text=f"Clients Connected: {len(self.client_sockets)}")

    def send_audio_file(self):
        file_name = "Ebaa.wav"
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                audio_data = f.read()
                data_packet = pickle.dumps(audio_data)
                message = struct.pack("Q", len(data_packet)) + data_packet
                with self.lock:
                    for client_socket in self.client_sockets:
                        client_socket.sendall(message)
            messagebox.showinfo("File Sent", f"The file '{file_name}' has been sent to clients.")
        else:
            messagebox.showerror("File Not Found", f"The file '{file_name}' does not exist.")

    def disconnect_all(self):
        with self.lock:
            while self.client_sockets:
                client = self.client_sockets.pop()
                client.close()
        self.server_socket.close()
        self.update_client_count()
        self.status_label.config(text="All clients disconnected")
        self.connect_button.config(state=tk.NORMAL)
        self.send_audio_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)
        messagebox.showinfo("Disconnection", "All clients disconnected and server stopped.")

if __name__ == "__main__":
    server_gui = ServerGUI()
    server_gui.root.mainloop()
