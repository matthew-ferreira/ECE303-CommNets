#Camille Chow and Matthew Ferreira
#Comm Nets Final Project

import logging
import socket
import time

import channelsimulator
import utils

import binascii
import sys


class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=0.001, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):
    TEST_DATA = bytearray([68, 65, 84, 65])  # some bytes representing ASCII characters: 'D', 'A', 'T', 'A'

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.put_to_socket(data)  # send data
                ack = self.simulator.get_from_socket()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class SenderV1(BogoSender):

    def __init__(self):
        super(SenderV1, self).__init__()

    def send(self, data):
        packet_length = 900
        num = (len(data) / packet_length) + 1
        while True:
            try:
                self.simulator.u_send(bytearray("1111111111" + "1"*11 + str(num)))
                ack = self.simulator.u_receive()
                if(str(ack[:10]) == "1111111111" and str(ack[10:]) == str(num)):
                    break
            except socket.timeout:
                pass

        packets = [[0 for x in range(num)] for y in range(4)]

        for x in range(num):
            packets[1][x] = str(x).zfill(10)
            packets[2][x] = str(binascii.crc32(data[(packet_length * x):(packet_length*(x+1))])).zfill(11)


        window_size = 10
        a,i = -1,0
        while a < num-1:
            while i - a <= window_size and i < num:
                self.simulator.u_send(bytearray(packets[1][i] + packets[2][i] + data[(packet_length * i):(packet_length*(i+1))]))
                self.logger.info("sending: " + packets[1][i])
                i+=1
            try:
                ack = self.simulator.u_receive()
                number = int(ack[0:10])

                if(number != 1111111111):
                    if(number == num and str(ack[:10]) == str(ack[10:])):
                        a = num
                    elif(str(ack[:10]) == str(ack[10:])):
                        packets[3][number] = True
                        while(packets[3][a+1] == True):
                            a+=1
                    
            except socket.timeout:
                i = a + 1
            except:
                pass

if __name__ == "__main__":
    sndr = SenderV1()

    data = sys.stdin.readlines()
    data = ''.join(data)
    
    sndr.send(data)
