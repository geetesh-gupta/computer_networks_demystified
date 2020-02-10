from constants import *
from node import Node


def main():
    node = None
    try:
        my_server_host = "localhost"
        my_server_port = int(input("Enter my server port: "))
        main_server_host = "localhost"
        main_server_port = int(input("Enter main server port: "))
        node = Node(my_server_host, my_server_port,
                    main_server_host, main_server_port)
        node.run()
        while True:
            # inp = input("Enter friend's port followed by request: ")
            inp = input()
            if inp == "continue":
                continue
            response = None
            code = int(inp.split(" ")[0])
            request = inp.split(" ")[1:]
            if code == 1:
                filename = request[0]
                filedata = " ".join(request[1:])
                response = node.create_new_file(filename, filedata)
                if response == "OK":
                    print("New file created")
                else:
                    print("Some error at the node")
            elif code == 2:
                # friends_host = request.split(' ')[0]
                friends_host = "localhost"
                friends_port = int(request[0])
                request = " ".join(request[1:])
                response = node.send_message(
                    request, friends_host, friends_port)
            elif code == 3:
                filename = request[0]
                response = node.search_file(filename)
                print("File response:", response)
                s_host, s_port = response.split(":")
                fileresp = node.request_file(s_host, int(s_port), filename)
                if fileresp == "OK":
                    print("New file created")
                else:
                    print("Some error at the node")

            print("Receiver response:", response)
    except (KeyboardInterrupt, SystemExit):
        if node is not None:
            node.exit_network()
        # print("Error in main file")
        sys.exit()
    except Exception as e:
        if node is not None:
            node.exit_network()
        print("Error in main file:", e)
        sys.exit()


if __name__ == "__main__":
    main()


# TODO: Add error handling if server not running
