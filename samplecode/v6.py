#! /usr/bin/env python
from zeroconf import mcastsocket
import select, threading, time

def create(group='FF02:0:0:0:0:2:FF00::',port=5000):
    sock = mcastsocket.create_socket( 
        ('::',port), TTL=1, loop=True, 
        reuse=True, 
        family=mcastsocket.socket.AF_INET6 
    )
    mcastsocket.join_group( sock, group )
    return sock
def listen( sock, group='FF02:0:0:0:0:2:FF00::' ):
    try:
        for i in range( 20 ):
            rs,wr,xs = select.select( [sock],[],[], .05 )
            if rs:
                data, addr = sock.recvfrom( 65500 )
                print 'From:', addr 
                print repr(data)
                return
    finally:
        mcastsocket.leave_group( sock, group )

def send( sock, data, group='FF02:0:0:0:0:2:FF00::', port=5000 ):
    try:
        for i in range(5):
            sock.sendto( data, (group,port))
    finally:
        mcastsocket.leave_group( sock, group )

def main():
    s1 = create( )
    s2 = create( port=5001 )
    t = threading.Thread( target=listen, args=(s1,)).start()
    send( s2, 'hello world' )

if __name__ == "__main__":
    main()
