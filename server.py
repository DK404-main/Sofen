import socket
import threading as t
from random import randint


server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
machine_address = ("localhost", 38385)
clients = []
messages = []
chats = []
tracking = []

for index_chat in range(0,3):
    chat_id = ''.join([*map(str, [randint(0,9) for _ in range(0,12)])])
    chat_tag = ''.join(["socketchat"[randint(0,9)] for _ in range(0,5)])
    chats += [{"chat_name": f"Chat_{index_chat}",
               "chat_id": chat_id,
               "chat_tag": chat_tag,
               "members": []}]
for chat in chats:
    print(f"----------------\n|Chat name: {chat['chat_name']}\n|ID-chat: {chat['chat_id']}\n|Chat tag: {chat['chat_tag']}\n----------------")

server_sock.bind(machine_address)
server_sock.listen(2)

print("Waiting connection...")


def server_work():
    global clients, messages
    while 1:
        for message in messages:
            if message["is_read"] == 0:
               message["is_read"] = 1
               print(f"Client {message['author']} sent message:\n->{message['message']}\n")


def connector_c():
    global clients, tracking
    while 1:
        connection, addr = server_sock.accept()
        if addr != None:
            print("Connected:", addr)
            ID_user = connection.recv(1024)
            clients += [{"ID_user": ID_user, "addr": addr, "connection": connection}]
            recv_messages_from_client = t.Thread(target=recviving_messages_from_clients, args=[[connection,addr, ID_user, ""]])
            recv_messages_from_client.start()
            recv_messages_from_client.join()
            tracking += [recv_messages_from_client]


def recviving_messages_from_clients(data):
    global messages
    if len(data)!=0:
        id_user = data[2].decode()
        while 1:
            if data[3]!="":
                data[0].sendto("CODE:201".encode(), data[0])
                messages += [{"author": id_user,
                            "message": data[0].recv(1024).decode(),
                            "is_read": 0,
                            "chat_id": data[3]}]
            else:
                data[0].sendto(f"100#{chats}".encode(), data[1])
                chat_choice = data[0].recv(1024).decode()
                data[3] = [chat["chat_id"] for chat in chats if chat["chat_name"]==chat_choice][0]
                data[0].sendto(data[3].encode(), data[1])
    else:
        ...

                
if __name__ == "__main__":
    connector_clients = t.Thread(target=connector_c) 
    connector_clients.start()
    connector_clients.join()
    print("Connector clients | Working")
    
    server_working = t.Thread(target=server_work)
    server_working.start()
    server_working.join()
    print("Server work | Starting")

    recv_messages_from_client = t.Thread(target=recviving_messages_from_clients)
    recv_messages_from_client.start()
    recv_messages_from_client.join()
    print("Recv messages from clients | Started")

