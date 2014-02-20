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
        print "1. Testing registration of a service..."
        desc = {'version':'0.10','a':'test value', 'b':'another value'}
        info = ServiceInfo(
            "_http._tcp.local.", "My Service Name._http._tcp.local.",
            socket.inet_aton(host_ip), 1234, 0, 0, desc
        )
        print "   Registering service..."
        r.registerService(info)
        print "   Registration done."
        
        print "2. Testing query of service information..."
        service_info = r.getServiceInfo("_http._tcp.local.", "coolserver._http._tcp.local.")
        print "   Getting 'coolserver' service: %r" % service_info
        if service_info is None:
	  print "       (Did you expect to see here the details of the 'coolserver' service? Try running 'nameprobe.py' before!)"
        print "   Query done."
        
        print "3. Testing query of own service..."
        my_service = r.getServiceInfo("_http._tcp.local.", "My Service Name._http._tcp.local.")
        print "   Getting self:", str(my_service)
        print "   Query done."
        
        raw_input( 'Press <enter> to release name > ' )
        
        print "4. Testing unregister of service information..."
        r.unregisterService(info)
        print "   Unregister done."
    finally:
        r.close()

if __name__ == '__main__':
    logging.basicConfig( level = logging.INFO )
    usage = 'testmdnssd.py [ip.address]'
    sys.exit( main(*sys.argv[1:]) )
