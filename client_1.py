import socket
from random import randint

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 38385)
id_user = ''.join([*map(str, [randint(0,9) for _ in range(0,10)])])
user = [id_user]
chats = []
chat_id_now = ''

while 1:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            sock.sendall(user[0].encode())
            print(f"Connected to server({server_address})")
            while 1:
                if chat_id_now!="":
                    message = input("Txt: ").encode()
                    sock.sendto(message, server_address)
                    print(f"Message '{message.decode()}' are sent.")
                else:
                    code, chats = sock.recv(10024).decode().split("#")
                    exec("chats={chats}")
                    print(exec(*chats))
                    for chat in chats:
                        print(f"----------------\n|Chat name: {chat[0]}\n|ID-chat: {chat[1]}\n|Chat tag: {chat[3]}\n----------------")
                    choice = input("Enter server tag: ").encode()
                    sock.sendto(choice, server_address)
                    chat_id_now = sock.recv(1024).decode()
    except ConnectionResetError:
        print("Connection closed | Side: server.")

