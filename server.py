import socket
import threading as t
from random import randint


server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
machine_address = ("localhost", 38385)


class Server_data():
    clients = []
    messages = []
    chats = []
    tracking = []

    
for index_chat in range(0,3):
    chat_id = ''.join([*map(str, [randint(0,9) for _ in range(0,12)])])
    chat_tag = ''.join(["socketchat"[randint(0,9)] for _ in range(0,5)])
    Server_data.chats += [{"chat_name": f"Chat_{index_chat}",
               "chat_id": chat_id,
               "chat_tag": chat_tag,
               "chat_members": [],
                "chat_messages": []}]

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
            ID_user = connection.recv(1024).decode()
            Server_data.clients += [{"user_id": ID_user, "addr": addr, "connection": connection, "chat_now": [], "chat_list": []}]
            recv_messages_from_client = t.Thread(target=recviving_messages_from_clients, args=[[connection, addr, ID_user, ""]]) #FORM [CONNECTION, addr, ID_user, chat]
            recv_messages_from_client.start()
            recv_messages_from_client.join()
            Server_data.tracking += [recv_messages_from_client]


def recviving_messages_from_clients(data):
    global Server_data
    if len(data)!=0:
        id_user = data[2]
        while 1:
            if len(data[3])!=0:
                "Створення та відправка повідомлень у різні чати"
                data[0].sendto("CODE:201".encode(), data[1])
                exec(f"chat_id={data[3]}")
                for chat in Server_data.chats:
                    if chat["chat_id"] == chat_id:
                        message_id = ''.join([*map(str, [randint(0,9) for _ in range(0,10)])])
                        chat["chat_messages"] += [{"author": id_user,
                                "message": data[0].recv(1024).decode(),
                                "is_read": [],
                                "message_id": message_id}]
                for message in Server_data.messages:
                    data[0].sendto(f"100#{Server_data.chats}".encode(), data[1])
            else:
                "Запрос на підключення користувача до бажанного чату"
                data[0].sendto(f"200#{Server_data.chats}".encode(), data[1])
                chat_choice = data[0].recv(1024).decode()
                data[3] = f"{[chat for chat in Server_data.chats if chat['chat_tag']==chat_choice][0]}"
                data[0].sendto(data[3].encode(), data[1])
                for client in Server_data.clients:
                    if client["user_id"]==data[2]:
                        for chat in Server_data.chats:
                            if chat["chat_tag"]==chat_choice:
                                chat["chat_members"] += [id_user]
                                client["chat_now"] = chat["chat_id"]
                                client["chat_list"] += [chat["chat_id"]]
                                break
                        
    else:
        ...

                
if __name__ == "__main__":
    connector_clients = t.Thread(target=connector_c) 
    connector_clients.start()
    connector_clients.join()
    print("Connector clients | Working")
    
    load_messages = t.Thread(target=load_messages_from_chat)
    load_messages.start()
    load_messages.join()
    print("Load message from chat | Starting")

    recv_messages_from_client = t.Thread(target=recviving_messages_from_clients)
    recv_messages_from_client.start()
    recv_messages_from_client.join()
    print("Recv messages from clients | Started")

