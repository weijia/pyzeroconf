

#Ref: https://code.google.com/p/volatility/issues/detail?id=74
#Ref: https://gist.github.com/nnemkin/4966028
import socket

try:
    import socket
    inet_ntop = socket.inet_ntop
    inet_pton = socket.inet_pton
except:
    # This software released into the public domain. Anyone is free to copy,
    # modify, publish, use, compile, sell, or distribute this software,
    # either in source code form or as a compiled binary, for any purpose,
    # commercial or non-commercial, and by any means.

    import socket
    import ctypes

    class sockaddr(ctypes.Structure):
        _fields_ = [("sa_family", ctypes.c_short),
                    ("__pad1", ctypes.c_ushort),
                    ("ipv4_addr", ctypes.c_byte * 4),
                    ("ipv6_addr", ctypes.c_byte * 16),
                    ("__pad2", ctypes.c_ulong)]

    WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
    WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA

    def inet_pton(address_family, ip_string):
        addr = sockaddr()
        addr.sa_family = address_family
        addr_size = ctypes.c_int(ctypes.sizeof(addr))

        if WSAStringToAddressA(ip_string, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
            raise socket.error(ctypes.FormatError())

        if address_family == socket.AF_INET:
            return ctypes.string_at(addr.ipv4_addr, 4)
        if address_family == socket.AF_INET6:
            return ctypes.string_at(addr.ipv6_addr, 16)

        raise socket.error('unknown address family')

    def inet_ntop(address_family, packed_ip):
        addr = sockaddr()
        addr.sa_family = address_family
        addr_size = ctypes.c_int(ctypes.sizeof(addr))
        ip_string = ctypes.create_string_buffer(128)
        ip_string_size = ctypes.c_int(ctypes.sizeof(addr))

        if address_family == socket.AF_INET:
            if len(packed_ip) != ctypes.sizeof(addr.ipv4_addr):
                raise socket.error('packed IP wrong length for inet_ntoa')
            ctypes.memmove(addr.ipv4_addr, packed_ip, 4)
        elif address_family == socket.AF_INET6:
            if len(packed_ip) != ctypes.sizeof(addr.ipv6_addr):
                raise socket.error('packed IP wrong length for inet_ntoa')
            ctypes.memmove(addr.ipv6_addr, packed_ip, 16)
        else:
            raise socket.error('unknown address family')

        if WSAAddressToStringA(ctypes.byref(addr), addr_size, None, ip_string, ctypes.byref(ip_string_size)) != 0:
            raise socket.error(ctypes.FormatError())

        return ip_string[:ip_string_size.value]


