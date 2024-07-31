import socket
import re
import threading



# Define socket host and port
SERVER_HOST = 'localhost'
SERVER_PORT = 4221

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))


# server_socket.listen(1)
# print('Listening on port %s ...' % SERVER_PORT)
# server_socket = socket.create_server(("localhost", 4221), reuse_port=True)



def construct_response(status_line, headers, response_body):

    # first let's take care of the headers 
    result = []

    for key, val in headers.items():
        temp = ' '.join([key, val])
        result.append(temp)
    # print(result)
    final = '\r\n'.join(result) + '\r\n'

    # print(final)
    result = '\r\n'.join([status_line, final, response_body])

    return result.encode()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        request = conn.recv(1024).decode()
        request_split = str(request).split("\r\n")
        print(request_split)
        pattern = "^GET (.+) HTTP/1.1"
        x = re.findall(pattern, request_split[0])
        print(x)

        # Send HTTP response
        if x[0] == '/':
            response = b'HTTP/1.1 200 OK\r\n\r\n'
        elif (x[0][0:6] == '/echo/'):
            print(x[0][6:])
            status = 'HTTP/1.1 200 OK'
            headers = {
                'Content-Type:': 'text/plain',
                'Content-Length:': str(len(x[0][6:]))
            }
            body = x[0][6:]

            response = construct_response(status, headers, body)
            # response = b'HTTP/1.1 200 OK\r\n\r\n'
        elif x[0] == '/user-agent':
            pattern = r'User-Agent: (.+?)\r\n'
            match = re.search(pattern, request)
            if match:
                user_agent = match.group(1)
                print("request object text: ", request)
                print(type(user_agent))
                print("User-Agent: ", user_agent)
                status = 'HTTP/1.1 200 OK'
                headers = {
                    'Content-Type:': 'text/plain',
                    'Content-Length:': str(len(user_agent))
                }
                body = user_agent
                response = construct_response(status, headers, body)
                print(r"RESPONSE: \n", response.decode())
            else:
                print("User-Agent header not found ! ! ! ")
        else:
            response = b'HTTP/1.1 404 Not Found\r\n\r\n'

        print("RESPONSE:   ", response)
        conn.sendall(response)
        # client_connection.close()
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg_length:
        #     msg_length = int(msg_length)
        #     msg = conn.recv(msg_length).decode(FORMAT)
        #     if msg == DISCONNECT_MESSAGE:
        #         connected = False
        #     print(f"[{addr}] {msg}")
        # conn.send("Msg received".encode(FORMAT))
    conn.close()



def server():
    server_socket.listen()
    print(f"[LISTENING] Server is listening .....")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def main():
    print("[STARTING] server is starting...")
    server()

if __name__ == "__main__":
    main()
