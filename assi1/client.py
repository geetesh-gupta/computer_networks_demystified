from constants import *


class Client:

    def __init__(self, my_friends_host, my_friends_port, request):
        # print("Client started...")
        self.host = my_friends_host
        self.port = my_friends_port
        self.request = request
        self.response = "DEFAULT"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        try:
            self.s.connect((self.host, self.port))
            # print("Requesting", self.request)
            self.request += ":END"
            self.s.sendall(self.request.encode(ENCODING))
            # print("Waiting for response")
            self.response = self.s.recv(1024).decode(ENCODING)
            # print("Response received")
            self.s.shutdown(2)
            self.s.close()
        except Exception as e:
            print("Error at client side:", e)
            sys.exit()

    def get_response(self):
        return self.response


if __name__ == "__main__":
    # host = input("Enter the host of server: ")
    # port = input("Enter the port of server: ")
    client = Client('localhost', 1234)
