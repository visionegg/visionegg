#!/usr/bin/env python

import sys,re,random
from socket import *

PORT = 50003
BUFSIZE = 1024
dig_pattern = 'digitize\((.+),(.+),(.+),(.+)\)'
gain_pattern = 'gain\((.+)\)'

CRLF = '\r\n'

fake_data_start ='BEGIN ASCII DATA (32 bit big-endian signed int)'+CRLF


fake_data_end = 'END ASCII DATA'+CRLF

##class debug_socket(socket):
##    def send(self,string):
##        print "SEND",string
##        apply(socket.send,(self,string))

##    def recv(self,bufsize):
##        results = apply(socket.recv,(self,bufsize))
##        print "RECV============"
##	print results
##	print "================"
##	if len(results) < 10:
##		for i in range(len(results)):
##			print "%X"%ord(results[i]),
##		print
##	else:
##		print "(too long!)"
##	print "================"
##        return results

class debug_socket2:
    def __init__(self,real):
        self.real = real
        self.send = real.send

    def recv(self,bufsize):
        results = self.real.recv(bufsize)
        print "RECV============"
	print results
	print "================"
	if len(results) < 10:
		for i in range(len(results)):
			print "%X"%ord(results[i]),
		print
	else:
		print "(too long!)"
	print "================"
        return results

def main():
    if len(sys.argv) > 1:
        port = int(eval(sys.argv[1]))
    else:
        port = PORT
##    s = debug_socket(AF_INET, SOCK_STREAM)
    s = socket(AF_INET, SOCK_STREAM)
    print sys.argv[0],"starting on port %d"%port
    s.bind(('', port))
    s.listen(1)
    conn, (remotehost, remoteport) = s.accept()
    conn_real = conn
    conn = debug_socket2(conn_real)
    print 'connected by', remotehost, remoteport
    conn.send('daqserv> ')
    while 1:
        data = conn.recv(BUFSIZE)
        if not data:
            break
        match = re.search(dig_pattern,data)
        if match:
            num_channels, sample_rate_hz, duration_sec, trigger_mode = match.group(1,2,3,4)
            num_channels = int(num_channels)
            sample_rate_hz = float(sample_rate_hz)
            duration_sec = float(duration_sec)
            trigger_mode = int(trigger_mode)
            conn.send('ready> ')
            while 1:
                data = conn.recv(BUFSIZE)
                match = re.search('go',data)
                if match:
                    conn.send(fake_data_start)
                    samples = sample_rate_hz * duration_sec
                    fake_data = ""
                    for i in range(samples):
                        for j in range(num_channels):
                            fake_data = fake_data + "%d\t"%random.gauss(0.0,2**8)
                        fake_data = fake_data[:-1] + CRLF
                        conn.send(fake_data)
                        #print fake_data
                        fake_data = ""
                    conn.send(fake_data_end)
                    break
                conn.send('ready> ')
        else:
            match = re.search(gain_pattern,data)
            if match:
                pass
            else:
                match = re.search('server quit',data)
                if match:
                    break
                else:
                    match = re.search('exit',data)
                    if match:
                        break

        conn.send('daqserv> ')

main()
