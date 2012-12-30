#! /usr/bin/env python
import socket
from zeroconf import mdns, mcastsocket, dns

fake_type = '_test-server.local.'

def main( base_name='coolserver.local.'):
    z = mdns.Zeroconf( '' )
    try:
        name = '%s.%s'%( base_name.split('.')[0], fake_type )
        s = dns.ServiceInfo(
            fake_type,
            name,
            server = base_name,
            address = socket.inet_aton('127.0.0.1'),
            port = 8080,
            properties = {},
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
