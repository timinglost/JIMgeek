import ipaddress
import os


def host_ping(ip_list):
    for i in ip_list:
        ipv4 = ipaddress.ip_address(i)
        ping_ip = os.system("ping -n 1 " + str(ipv4))
        if ping_ip == 0:
            print(f'{i}: Узел доступен')
        if ping_ip == 1:
            print(f'{i}: Узел недоступен')


if __name__ == '__main__':
    ip_list = ['192.168.0.1', '127.0.0.1', '192.168.1.255', '10.10.10.10', '255.255.255.0', '255.255.255.255', '127.0.0.2']
    host_ping(ip_list)
