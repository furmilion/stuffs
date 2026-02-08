import socket
import socketserver
import random



lst = [i for i in range(256)]
a1 = 1
a2 = 1
a3 = 0
a4 = 1
port = 1448

while 1:
    print(f'Attempting creating server at {a1}.{a2}.{a3}.{a4} at port {port}')
    try:
        with socket.create_server((f'{a1}.{a2}.{a3}.{a4}', port)) as server:
            server.close()
        print(f'Starting server at {a1}.{a2}.{a3}.{a4} at port {port}')
        break
    except OSError:
        a1 = (a1 + 1) & 0b11111111
with socket.create_server((f'{a1}.{a2}.{a3}.{a4}', port)) as server:
    print(server.getsockname())
    while 1:
        conn, addr = server.accept()
        print(conn, addr)

        #server.send(b'darta')
