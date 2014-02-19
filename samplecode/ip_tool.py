

#Ref: http://www.pythonclub.org/python-network-application/get-ip-address
try:
    import socket
    import fcntl
    import struct

    def get_ip_address(ifname="wlan0"):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

except:
    import socket

    def get_ip_address():
        myname = socket.getfqdn(socket.gethostname())
        myaddr = socket.gethostbyname(myname)
        return myaddr