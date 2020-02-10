from constants import *


class MainServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nodes = set()

    def add_node(self, node):
        self.nodes.add(node)
        print("Nodes present: ", self.nodes)

    def remove_node(self, node):
        self.nodes.remove(node)
        print("Nodes present: ", self.nodes)

    def get_random_node(self):
        if self.nodes:
            return random.choice(tuple(self.nodes))
        return None

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, self.port))
            sock.listen(10)
            print("Server started on ", (self.host, self.port))
            while True:
                connection, client_address = sock.accept()
                try:
                    request = ""
                    while True:
                        data = connection.recv(1024)
                        request = request + data.decode(ENCODING)
                        if request.split(':')[-1] == "END":
                            request = ":".join(request.split(":")[:-1])
                            break
                    sender_addr = None
                    # If client wants to disconnect
                    if request.split(':')[0] == 'QUIT':
                        print("Quit")
                        sender_addr = ":".join(request.split(":")[1:])
                        self.disconnect(sender_addr)
                    # If client wants to connect
                    else:
                        sender_addr = request
                        print(sender_addr, "connected to the network.")
                        random_node = self.get_random_node()
                        self.add_node(sender_addr)
                        # TODO: Add END flag here as well
                        if random_node is not None:
                            connection.sendall(random_node.encode(ENCODING))
                        else:
                            connection.sendall(
                                "No previous nodes exists".encode(ENCODING))
                except Exception as e:
                    print("Error transferring data from client:", e)
                    if request:
                        print("Message received:", request)
                    pass
                finally:
                    connection.shutdown(2)
                    connection.close()

        except KeyboardInterrupt:
            print("Server stopped without errors.")
            sys.exit()
        except Exception as e:
            print("Server stopped with error:", e)

    def disconnect(self, node):
        self.remove_node(node)
        print(node + " disconnected from the network.")


def main():
    # server_host = input("Enter server host: ")
    try:
        server_port = int(input("Enter server port: "))
        server = MainServer('localhost', server_port)
        # treads = [server.start()]
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped without errors.")
    except Exception as e:
        print("\nUnable to create server with error:", e)


if __name__ == '__main__':
    main()
