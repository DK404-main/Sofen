import socket
import threading as t
from random import randint
import sqlite3
import time

database = sqlite3.connect("messenger_base.db", check_same_thread=False)
cur = database.cursor()

database.execute("create table if not exists Users(user_nickname TEXT, user_tag TEXT, user_id INTEGER, user_mail TEXT, chat_now TEXT, chats_list TEXT, creation_date TEXT)")
database.execute("create table if not exists Chats(chat_title TEXT, chat_tag TEXT, chat_id INTEGER, chat_members TEXT, creation_date TEXT)")
database.execute("create table if not exists Messages(author_id INTEGER, chat_id INTEGER, message_id INTEGER, message_text TEXT, creation_date TEXT)")

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
machine_address = ("localhost", 38385)


class Server_data():
    clients = []
    messages = []
    chats = []
    tracking = []

#chat_id = ''.join([*map(str, [randint(0,9) for _ in range(0,12)])])
#chat_tag = ''.join(["socketchat"[randint(0,9)] for _ in range(0,5)])

server_sock.bind(machine_address)
server_sock.listen(2)

print("Waiting connection...")


def load_messages_from_chat():
    global Server_data
    "Загрузка повідомлень вибраних користувачем чатів"
    while 1:
        for chat in Server_data.chats:
            for member_id in chat["chat_members"]:
                members = [client for client in Server_data.clients if client["user_id"]==member_id]
                for member in members:
                    for message in chat["chat_messages"]:
                        if member["user_id"] not in message["is_read"]: 
                            member["connection"].sendto(message["message"].encode(), sock_member["addr"])
                            message["is_read"] += [member["user_id"]]


def connector_c():
    global Server_data
    "Приєднання користувачів до серверу"
    while 1:
        connection, addr = server_sock.accept()
        if addr != None:
            print("Connected:", addr)
            user_info = connection.recv(1024).decode().split("↔")
            cur.execute(f"SELECT * FROM Users WHERE user_id={user_info[2]}")
            info = cur.fetchone()
            if info==None:
                #Незареєстрований клієнт | Регістрація 
                database.execute(f'insert into Users(user_nickname, user_tag, user_id, user_mail, creation_date, chat_now, chats_list) VALUES("{user_info[0]}", "{user_info[1]}", "{user_info[2]}", "{user_info[3]}", "{user_info[4]}", "None", "");')
                database.commit()
                cur.execute(f"select * from Users where user_id={user_info[2]}")
                info = cur.fetchone()
                recv_messages_from_client = t.Thread(target=recviving_messages_from_clients, args=[info, [connection, addr]]) #FORM [CONNECTION, addr, ID_user, chat]
                recv_messages_from_client.start()
            else:
                #Зареєстрований клієнт | Авторизація
                cur.execute(f"select * from Users where user_id={user_info[2]}")
                info = cur.fetchone()
                recv_messages_from_client = t.Thread(target=recviving_messages_from_clients, args=[info, [connection, addr]]) #FORM [CONNECTION, addr, ID_user, chat]
                recv_messages_from_client.start()


def recviving_messages_from_clients(data_user, data_connection):
    global Server_data
    if len(data_connection)!=0:
        user_id = data_user[2]
        while 1:
            if data_user[4]!="":
                "Створення та відправка повідомлень у різні чати"
                cur.execute("SELECT * FROM Chats;")
                chats = [*{*cur.fetchall()}]
                data_connection[0].sendto(f"{chats}".encode(), data_connection[1])
                chat_id=data_user[4]
                cur.execute(f"SELECT chat_now FROM Users WHERE user_id={data_user[2]}")
                chat_id = cur.fetchone()[0]
                time_now = time.localtime()
                time_structurized = f"{time_now.tm_hour}:{time_now.tm_min}:{time_now.tm_sec}|{time_now.tm_mday}.{time_now.tm_mon}.{time_now.tm_year}"
                message_id = ''.join([*map(str, [randint(0,9) for _ in range(0,10)])])
                message_text = data_connection[0].recv(1024).decode()
                database.execute(f"INSERT INTO Messages VALUES('{user_id}','{chat_id}','{message_id}','{message_text}', '{time_structurized}');")
                database.commit()
            else:
                "Запрос на підключення користувача до бажанного чату"
                cur.execute("SELECT * FROM Chats;")
                chats = cur.fetchall()
                data_connection[0].sendto(f"{chats}".encode(), data_connection[1])
                chat_choice = data_connection[0].recv(1024).decode()
                choosed_chat_tag = chat_choice
                cur.execute(f"select * from Chats where chat_tag='{choosed_chat_tag}'")
                info_about_chat = cur.fetchall()[0]
                cur.execute(f"select chats_list FROM Users WHERE user_id='{user_id}'")
                chats_list = str(cur.fetchone())+str(info_about_chat[2])
                cur.execute(f"select chat_members FROM Chats WHERE chat_id='{info_about_chat[1]}'")
                chat_members = str(cur.fetchone()) + "|" + str(data_user[2])
                print(chats_list, chat_members)
                database.execute(f"UPDATE Users SET chat_now='{info_about_chat}', chats_list = '{chats_list.replace('[]', '')}' WHERE user_id='{data_user[2]}'")
                database.commit()
                database.execute(f"UPDATE Chats SET chat_members='{chat_members}' WHERE chat_id='{info_about_chat[2]}'")
                database.commit()
                data_connection[0].sendto(f"{info_about_chat}".encode(), data_connection[1])                  
    else:
        ...

                
if __name__ == "__main__":
    connector_clients = t.Thread(target=connector_c)
    connector_clients.start() 
    print("Connector clients | Working")
    
    load_messages = t.Thread(target=load_messages_from_chat)
    load_messages.start()
    print("Load message from chat | Starting")
    connector_c()
