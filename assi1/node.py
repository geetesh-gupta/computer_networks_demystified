from constants import *
from client import Client


class Node:
    def __init__(self, host, port, server_host, server_port):
        self.host = host
        self.port = port
        self.server_host = server_host
        self.server_port = server_port
        self.server = None
        self.new_existing_node = None
        self.neighbours = set()
        self.files = {}

    # Setup the server on node
    def setup_server(self):
        try:
            print("Server starting")
            self.server_thread = threading.Thread(
                target=self.listen, daemon=True)
            self.server_thread.start()
            print("Server started")
        except Exception as e:
            print("Error at setup_server:", e)
            sys.exit()

    # Request for any network's node
    def enter_network(self):
        try:
            print("Connecting with the main server")
            conn = Client(self.server_host, self.server_port, self.get_addr())
            response = create_thread(conn)

            # Add current node to neighbours list
            # self.neighbours.add(addr_str(self.host, self.port))

            # Print the response if no node exists in the network
            if len(response.split(':')) == 1:
                print("Main server response:", response)

            # Print the node addr if a node exists in the network
            if len(response.split(':')) != 1:
                self.new_existing_node = response
                print("Node returned by server:", self.new_existing_node)
                neighbour = self.fetch_conn_node(self.new_existing_node)
                # Connect with new neighbour and udpate their lists
                n_host, n_port = neighbour.split(':')
                n_response = self.send_message(
                    self.get_addr(), n_host, int(n_port), "ADD")
                if n_response == "OK":
                    self.neighbours.add(neighbour)
                print("Neighbours:", self.get_neighbours())
            print("Connected with network")
        except (KeyboardInterrupt, SystemExit):
            print("\n! Received keyboard interrupt, quitting threads.\n")
            self.exit_network()
            sys.exit()
        except Exception as e:
            print("Error at enter_network:", e)
            sys.exit()

    def fetch_conn_node(self, s_addr, c_addr=None):
        if c_addr is None:
            c_addr = self.get_addr()
        try:
            s_host, s_port = s_addr.split(":")
            sender_response = self.send_message(c_addr, get_host(s_addr), get_port(s_addr),
                                                "FETCH_NODE")
            print("Suitable node:", sender_response)
            return sender_response
        except (KeyboardInterrupt, SystemExit):
            self.exit_network()
            sys.exit()
        except Exception as e:
            print("Error at fetch_conn_node:", e)

    def exit_network(self):
        # Request for any network's node
        try:
            print("Disconnecting with main server")
            conn = Client(self.server_host, self.server_port,
                          "QUIT:" + self.host+":" + str(self.port))
            create_thread(conn)
            print("Disconnected from main server")
        except (KeyboardInterrupt, SystemExit):
            print("\n! Received keyboard interrupt, quitting threads.\n")
            sys.exit()
        except Exception as e:
            print("Error at exit_network:", e)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(10)
        try:
            while True:
                connection, client_address = sock.accept()
                c_thread = threading.Thread(
                    target=self.handle_request, args=(connection, client_address))
                c_thread.daemon = True
                c_thread.start()
        except Exception as e:
            print("Error in listen:", e)
            sys.exit()

    def handle_request(self, connection, addr):
        try:
            request = ""
            while True:
                data = connection.recv(1024)
                request = (request + data.decode(ENCODING)).strip()
                if request.split(':')[-1] == "END":
                    request = ":".join(request.split(":")[:-1])
                    break
            request = request.split(":")
            status = request[0]
            c_addr = ":".join(request[1:3])
            msg = ":".join(request[3:])

            if status == "FETCH_NODE":
                available_peer = None
                if self.conn_in_limit(self.neighbours):
                    available_peer = self.get_addr()
                else:
                    random_peer = random.choice(self.neighbours)
                    available_peer = self.fetch_conn_node(
                        random_peer, self.get_addr())
                connection.sendall(available_peer.encode(ENCODING))
            elif status == "ADD":
                self.neighbours.add(c_addr)
                print("Neighbours:", self.get_neighbours())
                connection.sendall("OK".encode(ENCODING))
            elif status == "SEND_MSG":
                print("Node "+c_addr+" sent: " + msg)
                connection.sendall(
                    "Message received by server".encode(ENCODING))
            elif status == "CREATE_FILE":
                filename = msg.split(":")[0]
                filedata = " ".join(msg.split(":")[1:])
                create_file(filename, self.get_addr(),
                            filedata.encode(ENCODING))
                self.register_file(filename, get_filepath(filename, self.get_addr()))
                connection.sendall("OK".encode(ENCODING))
            elif status == "SEARCH_FILE":
                filename = msg.split(":")[0]
                current_limit = int(msg.split(":")[1])
                if current_limit > 0:
                    response = self.check_filename(filename)
                    if response != "NOT_FOUND":
                        connection.sendall(response.encode(ENCODING))
                    else:
                        resp = self.search_file(filename, current_limit-1)
                        connection.sendall(resp.encode(ENCODING))
                else:
                    connection.sendall("NOT_FOUND".encode(ENCODING))
            elif status == "REQUEST_FILE":
                filename = msg
                filepath = self.files[filename]
                file = convert_to_bytes(filepath)
                connection.sendall(file.encode(ENCODING))
            else:
                pass
        except Exception as e:
            print("Some error occured at server side of the node: ", e)
            sys.exit()
        finally:
            connection.shutdown(2)
            connection.close()

    def send_message(self, msg, host, port, category="SEND_MSG"):
        try:
            msg = category+":"+self.get_addr()+":"+msg
            sender = Client(host, port, msg)
            sender_response = create_thread(sender)
            return sender_response
        except Exception as e:
            print("Error at send_message:", e)
            self.exit_network()

    def create_new_file(self, filename, filedata):
        try:
            sender_response = self.send_message(
                filename+":"+filedata, self.host, self.port, "CREATE_FILE")
            return sender_response
        except Exception as e:
            print("Error at create_new_file:", e)
            self.exit_network()

    def search_file(self, filename, search_limit=SEARCH_LIMIT):
        try:
            for neighbour in self.neighbours:
                print("Searching for", filename, "in:", neighbour)
                n_host, n_port = neighbour.split(":")
                response = self.send_message(
                    filename+":"+str(search_limit), n_host, int(n_port), "SEARCH_FILE")
                if response != "NOT_FOUND":
                    return response
            return "NOT_FOUND"
        except (KeyboardInterrupt, SystemExit):
            self.exit_network()
        except Exception as e:
            print("Error in Search File:", e)

    def request_file(self, host, port, filename):
        try:
            filedata = self.send_message(filename, host, port, "REQUEST_FILE")
            return self.create_new_file(filename, filedata)
        except (KeyboardInterrupt, SystemExit):
            self.exit_network()
        except Exception as e:
            print("Error in Search File:", e)

    def register_file(self, filename, filepath):
        self.files[filename] = filepath

    def check_filename(self, filename):
        if filename in list(self.files.keys()):
            return self.get_addr()
            # return self.get_addr()+":"+self.files[filename]
        return "NOT_FOUND"

    def set_filepaths(self):
        with get_all_filepaths(self.get_addr()) as filepaths:
            for filepath in filepaths:
                self.files[filepath.name] = filepath.path

    def get_addr(self):
        return addr_str(self.host, self.port)

    def get_neighbours(self):
        return self.neighbours

    def conn_in_limit(self, lis):
        return len(lis) < NODES_CONN_LIMIT

    def run(self):
        self.setup_server()
        self.enter_network()
        self.set_filepaths()
