import socket

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 38385)

while 1:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            print(f"Connected to server({server_address})")
            while 1:
                message = input("Txt: ").encode()
                sock.sendall(message)
                print(f"Message '{message.decode()}' are sent.")
                #message = sock.recv(1024)
                #print(f"Server sent message: '{message.decode()}'")
    except:
        print("Connection closed | Side: server.")

