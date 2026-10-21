import socket
from random import randint
import sqlite3
import time

database = sqlite3.connect("user_info.db")
cur = database.cursor()
database.execute("CREATE TABLE if not exists User(username TEXT, user_tag TEXT, user_id INTEGER, user_mail TEXT, chat_now TEXT, chat_list TEXT, creation_date TEXT);")
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 38385)

chats = []
chat_now = None
cur.execute("SELECT * FROM User")
info_user = cur.fetchone()

if info_user == None:
    print("REGISTRATION USER:")
    username = input("Username: ")
    user_tag = input("Tag: ")
    user_mail = input("Mail: ")
    user_password = input("Password: ")
    user_id = ''.join([*map(str, [randint(0,9) for _ in range(0,10)])])
    time_now = time.localtime()
    time_structurized = f"{time_now.tm_hour}:{time_now.tm_min}:{time_now.tm_sec}|{time_now.tm_mday}.{time_now.tm_mon}.{time_now.tm_year}"
    database.execute(f"INSERT INTO User(username, user_tag, user_id, user_mail, chat_now, chat_list, creation_date) VALUES('{username}', '{user_tag}', '{user_id}', '{user_mail}', 'None', '', '{time_structurized}');") #%(username, user_tag, user_id, user_mail, time_structurized)
    database.commit()
while 1:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            cur.execute("SELECT * FROM User;")
            info = cur.fetchone()
            info = "↔".join([*map(str, info)])
            sock.sendall(f"{info}".encode())
            print(f"Connected to server({server_address})")
            while 1:
                if chat_now!=None:
                    message = input("Txt: ").encode()
                    sock.sendto(message, server_address)
                    print(f"Message '{message.decode()}' are sent.")
                else:
                    chats = sock.recv(10024).decode()
                    exec(f"chats={chats}")
                    chats = [*{*chats}]
                    for chat in chats:
                        print(f"----------------\n|Chat name: {chat[0]}\n|Chat tag: {chat[1]}\n|Chat id: {chat[2]}\n----------------")
                    choice = input("Enter server tag: ").encode()
                    sock.sendto(choice, server_address)
                    chat_now = sock.recv(1024).decode()
                    exec(f"chat={chat_now}[0]")
                    print(f"Joined to chat('{chat[0]}').")
                    
    except ConnectionResetError:
        print("Connection closed | Side: server.")

