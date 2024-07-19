# Uncomment this to pass the first stage
# Another resource: 
# https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
# another source for a deep dive into networking: https://hpbn.co/#toc
import socket
import re


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # server_socket.accept() # wait for client

    while True:
        client_connection, client_address = server_socket.accept()
        print(client_address)
        print(client_connection)

        # Get the client request
        request = client_connection.recv(1024).decode()
        request_split = str(request).split("\r\n")
        print(request_split)
        pattern = "^GET (.+) HTTP/1.1"
        x = re.findall(pattern, request_split[0])
        print(x)

        # Send HTTP response
        if x[0] == '/':
            response = b'HTTP/1.1 200 OK\r\n\r\n'
        else:
            response = b'HTTP/1.1 404 Not Found\r\n\r\n'

        client_connection.sendall(response)
        client_connection.close()


if __name__ == "__main__":
    main()
