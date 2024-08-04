# Uncomment this to pass the first stage
# Another resource: 
# https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
# another source for a deep dive into networking: https://hpbn.co/#toc
# threading source: https://eecs485staff.github.io/p4-mapreduce/threads-sockets.html#sockets-and-waiting

import contextlib
import sys
import os
import socket
import re
import threading


# Define socket host and port
SERVER_HOST = 'localhost'
SERVER_PORT = 4221
# SERVER = ""
# Another way to get the local IP address automatically
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
print(socket.gethostname())
# ADDR = (SERVER, PORT)

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))


# server_socket.listen(1)
# print('Listening on port %s ...' % SERVER_PORT)
# server_socket = socket.create_server(("localhost", 4221), reuse_port=True)


def inpect_file(abs_path=None, file_name=None):
    ''' 
    Description
    -----------
    This method inspects the exitence of a file,
    reading its content if it exists and returning it.

    Parameters
    ----------
    abs_path : str
        the provided absolute path from the commandline
    file_name : str
        the provided filename
    
    Returns
    -------
    boolean
        True if the file exists and False if not.
    str
        if the file is present, the content of the file.
    int
        size of the target file in bytes
    '''
    is_present, file_path, file_content, file_size = False, None, None, None

    if abs_path and file_name:
    # check if the file name exists in the provided path
    # List contents of the provided absolute directory 
        try:
            with os.scandir(abs_path) as entries:
                for entry in entries:
                    if entry.name == file_name:
                        is_present = True
                        file_path = os.path.join(abs_path, entry.name)
                        file_size = os.path.getsize(file_path)
                        break
        except FileNotFoundError:
            print(f"The directory {abs_path} does not exist.")

    # Let's read the file content
    # Reading a file
    if is_present:
        with open(file_path, 'r') as file:
            file_content = file.read()
    
    return [is_present, file_content, file_size]

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

def handle_client(conn, addr, abs_path):
    print(f"[NEW CONNECTION] {addr} connected.")
    response = ""
    connected = True
    while connected:
        request = conn.recv(1024).decode()
        print(request)
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
        elif (x[0][0:7] == '/files/'):
            # handle FILE related requests
            query_file_name = x[0][7:]
            file_result = inpect_file(abs_path, query_file_name)
            if file_result[0]:
                # file exists + construct a response
                status = 'HTTP/1.1 200 OK'
                headers = {
                    'Content-Type:': 'application/octet-stream',
                    'Content-Length:': str(file_result[2])
                }
                body = file_result[1] # content of the file
                response = construct_response(status, headers, body)
            else:
                response = b'HTTP/1.1 404 Not Found\r\n\r\n'
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



def server(abs_path):
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, abs_path))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def main():
    print("[STARTING] server is starting...")
    args = sys.argv
    abs_path = ""
    if len(args) > 1:
        with contextlib.suppress(ValueError):
            flag_index = args.index("--directory") 
            if len(args) > flag_index + 1:
                abs_path = args[flag_index + 1]
    
    if not abs_path:
        print("Provided Path is---  ", abs_path)

    server(abs_path)

if __name__ == "__main__":
    main()
