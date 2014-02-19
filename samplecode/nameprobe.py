#! /usr/bin/env python
import socket
from ip_tool import get_ip_address
from zeroconf.dns import ServiceInfo
from zeroconf.mdns import Zeroconf


def main( base_name='coolserver.local.', stype="_http._tcp.local."):
    # http://serverfault.com/questions/78048/whats-the-difference-between-ip-address-0-0-0-0-and-127-0-0-1
    z = Zeroconf( "0.0.0.0" ) # 0.0.0.0 represents all IP addresses on the local machine
    try:
        name = '%s.%s'%( base_name.split('.')[0], stype )
        s = ServiceInfo(
            stype,
            name,
            server = base_name,
            address = socket.inet_aton(get_ip_address()),
            port = 8080,
            properties = {"hello":"world", "dept":"deustotech"}, # Setting DNS TXT records...
        )
        
        z.registerService( s )
        name = z.probeName( base_name )
        z.unregisterService( s )
        print 'Negotiated name:', name
        s.server = name 
        z.checkService( s )
        z.registerService( s )
        raw_input( 'Press <enter> to release name > ' )
    finally:
        z.close()

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig( 
        #level = logging.DEBUG 
    )
    if sys.argv[1:]:
        name = sys.argv[1]
    else:
        name = 'coolserver.local.'
    main(name)
