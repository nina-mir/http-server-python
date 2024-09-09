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
import gzip


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

    # check if response is supposed to have a body in gzip
    if 'gzip' in final:            
        result = str.encode(status_line) + b"\r\n" + str.encode(final) + response_body
        return result

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

        # To-DO 
        # Figure out if this is a POST request or GET
        # if GET request, do the handle_GET()
        # If POST, do the post request handle_POST()

        print(request_split)

        response = ""
        http_verb = ""
        
        if len(request_split) > 0:
            http_verb = request_split[0].split(" ")
        if len(http_verb) > 0:
            http_verb = http_verb[0]
        
        if http_verb == 'GET':
            pattern = "^GET (.+) HTTP/1.1"
            x = re.findall(pattern, request_split[0])
            print("x is: ", x)
            response = handle_GET(request, x, abs_path)
        elif http_verb == 'POST':
            response = handle_POST(request, request_split, abs_path)


        print("RESPONSE:   ", response)
        conn.sendall(response)
        '''
        # client_connection.close()
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg_length:
        #     msg_length = int(msg_length)
        #     msg = conn.recv(msg_length).decode(FORMAT)
        #     if msg == DISCONNECT_MESSAGE:
        #         connected = False
        #     print(f"[{addr}] {msg}")
        # conn.send("Msg received".encode(FORMAT))'''

    conn.close()

def handle_GET(request, x, abs_path):
# Send HTTP response
    print("GET request being handled ...")
    if x[0] == '/':
        response = b'HTTP/1.1 200 OK\r\n\r\n'
    elif (x[0][0:6] == '/echo/'):
        print("echo message: ", x[0][6:])
        
        status = 'HTTP/1.1 200 OK'

        headers = {
            'Content-Type:': 'text/plain',
            'Content-Length:': str(len(x[0][6:]))
        }
        body = x[0][6:]

        # 1) To-DO write logic to detect Accept-Encoding
        pattern = r'Accept-Encoding: (.+?)\r\n'
        match = re.search(pattern, request)
        if match:
            compression_scheme = match.group(1)
            # To-DO: figure out if this is a comma seperated list of not
            if "gzip" in compression_scheme:
                new_item = {'Content-Encoding:': 'gzip'}
                headers.update(new_item)
                utf_encoded = gzip.compress(body.encode())
                print("UTF_encoded: ", utf_encoded)
                length_str = len(utf_encoded)
                body = utf_encoded.hex()
                print("hex body: ", body)
                # to-DO: modify the length of content-length header
                headers['Content-Length:'] = str(length_str)
                

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

    return response

def handle_POST(request, request_split, abs_path):
# To-DO 1) extract the filename from the request body
    pattern = r'/files/(.*) '
    file_to_write = re.findall(pattern, request_split[0])
    print("file to be created is called: ", file_to_write)
# To-DO 2) Extract the byte size of the message 
    pattern = r'Content-Length:\s*(\d+)'
    byte_to_write = re.findall(pattern, request)
    print("Bytes to write to file:  ", byte_to_write)

# To-Do 3) Extract the body of the file from the request 
    file_body = request_split[-1]
    print("content of file is: ", file_body)

# To-Do 4-a) create a file and write to disk 
    file_path = os.path.join(abs_path, file_to_write[0])
    with open(file_path, 'w') as f:
        f.write(file_body)
    f.close()

# To-Do 4-b) send a response back 
    return b'HTTP/1.1 201 Created\r\n\r\n'





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
