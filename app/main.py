# Uncomment this to pass the first stage
# Another resource: 
# https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
# another source for a deep dive into networking: https://hpbn.co/#toc
import socket
import re

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

        #TODO create a handle_request function
        
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
                user-agent = match.group(1)
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

        client_connection.sendall(response)
        client_connection.close()


if __name__ == "__main__":
    main()