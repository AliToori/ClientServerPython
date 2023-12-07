#!/usr/bin/env python3
from datetime import datetime, timedelta
import socket
import sys
import time
import io
import matplotlib.pyplot as plt
import numpy as np


def show_plot(measurement_type, values_calculated_from_response):
    title = ""
    if measurement_type == "rtt":
        title = "RTT_Table Number_Of_Probes Estimated_Rtt"
    elif measurement_type == "tput":
        title = "Throughput_Table Number_Of_Probes Throughput"
    # Initialize a plot
    plt.title(title)
    plt.plot(data=values_calculated_from_response)
    plt.show()


class Client:
    def __init__(self):
        """ from the command line user should provide the hostname of the server """
        # Bind the socket to the address given on the command line
        # server_name = sys.argv[1]
        # port_number = sys.argv[2]
        # server_address = (server_name, port_number)
        port_number = int(input("Enter the port number of the server: "))
        size = 0
        sum = 0
        """ use the hostname and the port number to create a client socket to connect to server """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', port_number))
            connection_setup = input("Please enter the Protocol Phase \"s\" for connection setup:")
            measurement_type = input("Please enter measurement type 'rtt' or 'tput':")
            number_of_probes = int(input("Please enter the number of the probes. It should be at least 10: "))
            if measurement_type == "rtt":
                size = int(input("Enter the size of the message. It should be 1, 100, 200, 400, 800 or 1000 bytes.\nType just 1,100,200,400,800 or 1000: "))
            elif measurement_type == "tput":
                size = int(input("Enter the size of the message. It should be 1K, 2K, 4K, 8K, 16K or 32K bytes.\nType just 1,2,4,8,16 or 32: "))
                size = size * 1000
            server_delay = int(input("Please enter server delay: "))
            protocol = connection_setup + " " + measurement_type + " " + str(number_of_probes) + " " + str(size) + " " + str(server_delay) + " " + '\n'
            sock.sendall(bytes(protocol, "utf-8"))
            print('************** MESSAGE HAS BEEN SENT TO THE SERVER **************')
            while True:
                answer = sock.recv(1024).decode("utf8")
                print("Server response: ", answer)
                values_calculated_from_response = [None] * number_of_probes
                if answer == "200 OK: Ready":
                    terminated = False
                    msg_to_sent = bytes(protocol, "utf-8")
                    for i in range(int(number_of_probes)):
                        message_phase_sequence = input(
                            "Please enter the Protocol Phase \"m\" for sending one message and the correct sequence probe for sending the message.It should be: " + str(
                                i + 1))
                        before_sent = datetime.now().microsecond/1000
                        msg = message_phase_sequence + str(msg_to_sent) + '\n'
                        sock.sendall(bytes(msg, "utf-8"))
                        after_sent = datetime.now().microsecond/1000
                        time = after_sent
                        print("Time is: " + str(time) + " Milliseconds")
                        print("Message from server: " + str(answer))
                        if measurement_type == "rtt":
                            estimated_rtt = time
                            values_calculated_from_response[i] = estimated_rtt
                            sum += estimated_rtt
                            print("Estimated RTT for probe: " + str((i + 1)) + " is " + str(estimated_rtt) + "Milliseconds")
                        elif measurement_type == "tput":
                            tput = (size / time)
                            values_calculated_from_response[i] = tput
                            sum += tput
                            print("Throughput for probe: " + str((i + 1)) + " is " + str(tput) + " Bps")
                        if answer == "404 ERROR: Invalid Measurement Message":
                            print("Invalid Measurement Message.\nTerminating the connection")
                            # close the connection to server
                            print("Connection with the server is closed.")
                            terminated = True
                            break
                    if measurement_type == "rtt":
                        print("The average RTT is " + (sum / number_of_probes) + " sec \n")
                    elif measurement_type == "tput":
                        print("The average Throughput is: " + (sum / number_of_probes) + " Bps \n")
                    if not terminated:
                        sock.sendall(bytes("t" + '\n', "utf-8"))
                        from_server = sock.recv(1024)
                        if from_server == "t":
                            # close the connection to server
                            break
                            print("Connection with the server is closed.")

                    # show_plot(measurement_type, values_calculated_from_response)
                elif answer == "404 ERROR: Invalid Connection Setup Message":
                    print("Connection setup is invalid or incomplete.\nTerminating the connection")
                    # close the connection to server
                    break
                    print("Connection with the server is closed.")
                if not answer:
                    break

    def recv_all(self, sock):
        total_data = []
        while True:
            data = sock.recv(1024).decode("utf8")
            if not data:
                break
            total_data.append(data)
        return ''.join(total_data)


client = Client()