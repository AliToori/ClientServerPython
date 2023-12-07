#!/usr/bin/env python3

import socket
import sys
import time


class Server:
    def __init__(self, port_number):
        self.port_number = port_number
        """ create the welcoming socket at port number provided by the user """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            """ waits a contact from a client """
            sock.bind(("localhost", self.port_number))
            # Listen for an incoming connection
            sock.listen(1)
            while True:
                # Wait for a connection
                print('waiting for a connection at ', sock.getsockname())
                connection, client_address = sock.accept()
                with connection:
                    print('Connection with client ' + str(client_address) + ' is established.')
                    # Receive the data in small chunks and retransmit it
                    while True:
                        protocol = connection.recv(1024).decode("utf8")
                        print('Protocol arrived from client: ' + str(protocol))
                        parts = protocol.split(" ")
                        protocol_phase = parts[0]
                        measurement_type = parts[1]
                        num_of_probes = int(parts[2])
                        print("*************************************************************", num_of_probes)
                        message_size = int(parts[3])
                        server_delay = int(parts[4])
                        if protocol_phase == "s" and (measurement_type == "rtt" or measurement_type == "tput") and (num_of_probes >= 10) and check_message_size(measurement_type, message_size) and server_delay >= 0:
                            if measurement_type == "rtt":
                                print("Client requires an RTT measurement type")
                            elif measurement_type == "tput":
                                print("Client requires an Throughput measurement type")
                            protocol_arrived_ok = "200 OK: Ready"
                            connection.sendall(bytes(protocol_arrived_ok, "utf8"))
                            for i in range(num_of_probes):
                                from_client = connection.recv(1024).decode("utf8")
                                print("Message from client: ", from_client)
                                if from_client is not None:
                                    parts_from_msg = from_client.split(" ")
                                    print("Message from client after splitting: ", parts_from_msg)
                                    protocol_phase_msg = parts_from_msg[0]
                                    probe = int(parts_from_msg[3])
                                    msg = int(parts_from_msg[4])
                                    time.sleep(server_delay)
                                    if protocol_phase_msg == "m" and probe == (i + 1) and msg == int(message_size):
                                        connection.sendall(bytes("This is an echo for message with probe number: " + probe + " with size: " + str(len(msg)) + '\n', "utf8"))
                                    else:
                                        message_arrived_error = "404 ERROR: Invalid Measurement Message"
                                        print("Terminating the connection with client ", connection.getsockname())
                                        connection.sendall(bytes(message_arrived_error + '\n', "utf8"))
                                        break
                                else:
                                    break
                            termination = connection.recv(1024).decode("utf8")
                            if termination == "t":
                                print("Terminating the connection with the client")
                                connection.sendall(bytes("t" + '\n', "utf8"))
                        else:
                            protocol_arrived_error = "404 ERROR: Invalid Connection Setup Message"
                            print("Terminating the connection with client ", connection.getsockname())
                            connection.sendall(bytes(protocol_arrived_error + '\n', "utf8"))
                        if not protocol:
                            break


def check_message_size(measurement_type, message_size):
    size = message_size
    if measurement_type == "rtt":
        if size == 1 or size == 100 or size == 200 or size == 400 or size == 800 or size == 1000:
            return True
        else:
            return False
    else:
        if size == 1000 or size == 2000 or size == 4000 or size == 8000 or size == 16000 or size == 32000:
            return True
        else:
            return False


port_number = int(input("Enter the port number for the server: "))
server = Server(port_number)
