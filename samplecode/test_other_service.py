#! /usr/bin/env python
import sys
import socket
import logging
from ip_tool import get_ip_address
from zeroconf.mdns import Zeroconf, ServiceInfo, __version__

# Test a few module features, including service registration, service
# query (for "coolserver"), and service unregistration.
# "coolserver" service can be registered running "nameprobe.py"

def main(ip=None):
    print "Multicast DNS Service Discovery for Python, version", __version__
    # It MUST be 0.0.0.0. NOT the local IP address or 127.0.0.1.
    # Otherwise, at least in GNU/Linux, it doesn't get the service
    # info of services registered in other processes (e.g. "coolserver")
    r = Zeroconf( "0.0.0.0" ) 
    #host_ip = socket.gethostbyname( socket.gethostname())
    host_ip = get_ip_address()
    try:
        
        print "1. Testing query of own service..."
        my_service = r.getServiceInfo("_test._tcp.local.", "AndroidTest._test._tcp.local.")
        print "   Getting self:", str(my_service)
        print "   Query done."
        
        raw_input( 'Press <enter> to release name > ' )

    finally:
        r.close()

if __name__ == '__main__':
    logging.basicConfig( level = logging.INFO )
    usage = 'testmdnssd.py [ip.address]'
    sys.exit( main(*sys.argv[1:]) )
