# Complex Engineering Activity, File Transfer System using SOCKET programming

#    Group Members
# Ebaa Haq (2021-CE-22)
# Maham Nadeem (2021-CE-10)
# Faiza Riaz (2021_CE-20)
# Sana Israr (2021-CE-55)

# This is client code to receive audio frames over TCP


import socket
import threading
import tkinter as tk
import wave
import pyaudio
import pickle
import struct
import os
import tkinter.messagebox as messagebox
import speech_recognition as sr


class ClientGUI:
    def __init__(self):
        self.host_name = socket.gethostname()
        self.host_ip = '10.5.152.164'  # Server IP address
        self.port = 9611
        self.client_socket = None

        self.root = tk.Tk()
        self.root.title("Client")
        self.status_label = tk.Label(self.root, text="Not Connected")
        self.status_label.pack()

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        self.stream_button = tk.Button(self.root, text="Start Streaming", state=tk.DISABLED,
                                       command=self.start_streaming)
        self.stream_button.pack()

        self.disconnect_button = tk.Button(self.root, text="Disconnect", state=tk.DISABLED, command=self.disconnect)
        self.disconnect_button.pack()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_address = (self.host_ip, self.port)
        self.client_socket.connect(socket_address)
        self.status_label.config(text="Connected to Server")
        self.connect_button.config(state=tk.DISABLED)
        self.stream_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.NORMAL)
        threading.Thread(target=self.receive_audio_file).start()
        messagebox.showinfo("Connection", "Connected to Server")

    def receive_audio_file(self):
        try:
            payload_size = struct.calcsize("Q")
            data = b""
            while len(data) < payload_size:
                packet = self.client_socket.recv(4 * 1024)  # 4K
                if not packet:
                    return  # No more data
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += self.client_socket.recv(4 * 1024)

            audio_data = pickle.loads(data[:msg_size])
            with open("received_audio.wav", "wb") as f:
                f.write(audio_data)
            # File is received, enable streaming button
            self.stream_button.config(state=tk.NORMAL)

            # Convert audio to text
            recognizer = sr.Recognizer()
            with sr.AudioFile("received_audio.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Save text to a text file
            with open("received_file.txt", "w") as text_file:
                text_file.write(text)
            messagebox.showinfo("Conversion", "Audio file converted to text and stored as received_file.txt")

        except Exception as e:
            messagebox.showerror("Error", f"Error receiving audio: {e}")

    def start_streaming(self):
        if os.path.exists("received_audio.wav"):
            threading.Thread(target=self.audio_stream).start()
            messagebox.showinfo("Streaming", "Received file is streaming")
        else:
            messagebox.showerror("File Not Found", "The received audio file does not exist.")

    def audio_stream(self):
        try:
            CHUNK = 1024
            wf = wave.open("received_audio.wav", 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            frames_per_buffer=CHUNK)
            data = wf.readframes(CHUNK)
            while data:
                stream.write(data)
                data = wf.readframes(CHUNK)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            messagebox.showinfo("Disconnection", "Disconnected from Server")
        self.status_label.config(text="Disconnected")
        self.connect_button.config(state=tk.NORMAL)
        self.stream_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    client_gui = ClientGUI()
    client_gui.root.mainloop()
