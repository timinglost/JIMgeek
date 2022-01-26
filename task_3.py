import ipaddress
import os
from tabulate import tabulate


def host_range_ping_tab(begin_ip, end_ip):
    begin_ip_count = int(begin_ip.split('.')[3])
    end_ip_count = int(end_ip.split('.')[3])
    all_ip_count = begin_ip.split('.')
    del all_ip_count[3]
    ip_list = []
    reachable = []
    unreachable = []
    while begin_ip_count <= end_ip_count:
        ip_list.append('.'.join(all_ip_count) + '.' + str(begin_ip_count))
        begin_ip_count += 1
    for i in ip_list:
        ipv4 = ipaddress.ip_address(i)
        ping_ip = os.system("ping -n 1 " + str(ipv4))
        if ping_ip == 0:
            reachable.append(str(i))
        if ping_ip == 1:
            unreachable.append(str(i))
    tuples_list = {'Reachable': reachable, 'Unreachable': unreachable}
    print(tabulate(tuples_list, headers="keys"))


if __name__ == '__main__':
    host_range_ping_tab('127.0.0.1', '127.0.0.5')
    host_range_ping_tab('10.10.10.5', '10.10.10.10')
