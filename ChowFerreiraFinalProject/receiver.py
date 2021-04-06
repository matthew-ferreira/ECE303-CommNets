#Camille Chow and Matthew Ferreira
#Comm Nets Final Project

import logging

import channelsimulator
import utils

import binascii
import sys

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            data = self.simulator.get_from_socket()  # receive data
            self.logger.info("Got data from socket: {}".format(
                data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
            self.simulator.put_to_socket(BogoReceiver.ACK_DATA)  # send ACK

class Receiver1(BogoReceiver):
    received_data = []
    
    def __init__(self):
        super(Receiver1, self).__init__()
        
    def receive(self):
        initialized = False
        rec = 0
        nmPckts = 10000
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))

        while rec < nmPckts:
            try:
                data = self.simulator.u_receive()  # receive data
                num = int(data[:10])
                crc = data[10:21]
                packet = data[21:]
                self.logger.info("Got packet number: " + str(num) + " with data: " + packet)
                if(initialized == False and num == 1111111111 and crc == "1"*11):
                    packet = int(packet)
                    self.simulator.u_send(bytearray(str(num) + str(packet)))
                    received_data = [0 for x in range(packet)]
                    nmPckts = packet
                elif (str(binascii.crc32(packet)).zfill(11) == str(crc)):
                    if(initialized == False):
                        self.logger.info("initialized")
                        initialized = True
                    if(received_data[num] == 0):
                        received_data[num] = str(packet)
                        rec += 1                        
                    self.logger.info("Send ack: " + str(num))
                    self.simulator.u_send(bytearray(str(num).zfill(10)+str(num).zfill(10)))
            except:
                pass
        y = str(nmPckts).zfill(10)
        for x in range(5):
            self.simulator.u_send(bytearray(y+y))
        
        sys.stdout.write(str(''.join(received_data)))
 

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = Receiver1()
    rcvr.receive()
