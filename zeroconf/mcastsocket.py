"""Multicast socket setup code

This is refactored from the Zeroconf.py main module to allow for reuse within
multiple environments (e.g. multicast SIP configuration, multicast paging
groups and the like).

You will need to be sure that your system is actually configured in such a way 
that it can properly receive and send multicast messages.

For instance, on Linux machines, the Reverse Path Filter feature in the kernel 
may prevent you from receiving messages from any sender for which you do not 
currently have a route defined (on a given interface).  This is particularly 
important if you are attempting to implement a protocol whose purpose is to 
allow machines to agree on an IP address without input from a DHCP server.

.. code-block:: bash

    $ echo "0" | sudo tee /proc/sys/net/ipv4/conf/eth0/rp_filter
    $ echo "0" | sudo tee /proc/sys/net/ipv4/conf/eth1/rp_filter

To create a multicast socket:

.. code-block:: python

    GROUP,PORT = ('224.1.1.2','8000')
    sock = mcastsocket.create_socket( ('0.0.0.0',PORT), loop=False )
    mcastsocket.join_group( sock, GROUP )
    try:
        sock.sendto( payload, (GROUP,PORT))
        while time.time() < timeout:
            rs,wr,xs = select.select( [sock],[],[], 5 )
            if rs:
                data, addr = sock.recvfrom( 65500 )
                if handle( sock, data, addr ):
                    break
    finally:
        mcastsocket.leave_group( sock, GROUP )

.. note::
    
    Multicast DNS Service Discovery for Python, v0.12
    Copyright (C) 2003, Paul Scott-Murphy

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""
import socket,logging
log = logging.getLogger( __name__ )

def create_socket( address, TTL=1, loop=True, reuse=True ):
    """Create our multicast socket for mDNS usage

    Creates a multicast UDP socket with ttl, loop and reuse parameters configured.

    * address -- IP address family address ('ip',port) on which to bind/broadcast,
                 The socket will *bind* on bind_address.  The IP_MULTICAST_IF
                 option will also be set to the ip specified.
    * TTL -- multicast TTL to set on the socket
    * loop -- whether to reflect our sent messages to our listening port
    * reuse -- whether to set up socket reuse parameters before binding

    returns socket.socket instance configured as specified
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, int(bool(loop)))
    allow_reuse( sock, reuse )
    limit_to_interface( sock, address[0] )
    try:
        # Note: multicast is *not* working if we don't bind on all interfaces, most likely
        # because the 224.* isn't getting mapped (routed) to the address of the interface...
        # to debug that case, see if {{{ip route add 224.0.0.0/4 dev br0}}} (or whatever your
        # interface is) makes the route suddenly start working...
        sock.bind(address)
    except Exception, err:
        # Some versions of linux raise an exception even though
        # the SO_REUSE* options have been set, so ignore it
        log.error('Failure binding: %s', err)
    return sock

def limit_to_interface( sock, interface_ip ):
    """Restrict multicast operation to the given interface/ip (instead of using routing)

    Sets the IP_MULTICAST_IF option on the socket to restrict multicast
    operations to a particular interface.  This is done without reference
    to the system routing tables, so you do not need to set up a 224.0.0.0/4
    route on the system to receive multicast on the interface.
    """
    if interface_ip and interface_ip != '0.0.0.0':
        # listen/send on a single interface...
        log.debug( 'Limiting multicast to use interface of %s', interface_ip )
        sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
            socket.inet_aton( interface_ip)
        )
        return True
    return False

def allow_reuse( sock, reuse=True ):
    """Setup reuse parameters on the given socket

    The common case where e.g. the host system has avahi or mdnsresponder
    installed will mean that our mDNS or uPNP port is likely already bound.
    This operation sets reuse options so that we can re-bind to the port.
    """
    if reuse:
        log.debug( 'Setting address/port reuse on mcast socket' )
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError, err:
            # ignore common case where SO_REUSEPORT isn't provided on Linux
            if err.args[0].find('SO_REUSEPORT') > -1:
                pass
            else:
                raise
        except Exception, err:
            # SO_REUSEADDR should be equivalent to SO_REUSEPORT for
            # multicast UDP sockets (p 731, "TCP/IP Illustrated,
            # Volume 2"), but some BSD-derived systems require
            # SO_REUSEPORT to be specified explicity.  Also, not all
            # versions of Python have SO_REUSEPORT available.  So
            # if you're on a BSD-based system, and haven't upgraded
            # to Python 2.3 yet, you may find this library doesn't
            # work as expected.
            log.debug( 'Ignoring likely spurious error on setting reuse options: %s', err )
        return True
    return False

def join_group( sock, group ):
    """Add our socket to this multicast group"""
    log.info( 'Joining multicast group: %s', group )
    sock.setsockopt(
        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(group) + socket.inet_aton('0.0.0.0')
    )
def leave_group( sock, group ):
    """Remove our socket from this multicast group"""
    log.info( 'Leaving multicast group: %s', group )
    sock.setsockopt(
        socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP,
        socket.inet_aton(group) + socket.inet_aton('0.0.0.0')
    )
