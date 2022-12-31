#!/usr/bin/env python3

import argparse

from scapy.fields import BitField
from scapy.all import (
    IP,
    UDP,
    Ether,
    Packet,
    bind_layers,
    get_if_addr,
    get_if_hwaddr,
    get_if_list,
    sendp
)

from utils.TopologyParser import TopologyParser


class SourceRoute(Packet):
    fields_desc = [BitField('bos',  0,  1), 
                   BitField('port', 0, 15)]


def parse_args():
    parser = argparse.ArgumentParser(description='P4 Source Routing Sender')
    parser.add_argument('-t', '--target', type=str, required=True,  metavar='<dst>', 
                        help='the target IP address or the target host name')
    parser.add_argument('-T', '--topo-path', type=str, required=False, default='topo/topology.json', metavar='<path>', 
                        help='path to the json topology file')
    parser.add_argument('-i', '--interface', type=str, required=False, default='eth0', dest='iface', metavar='<iface>', 
                        help='the gateway interface name')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    assert args.iface in get_if_list(), f"interface '{args.iface}' is not in the list"

    bind_layers(Ether,       SourceRoute, type=0x1234)
    bind_layers(SourceRoute, SourceRoute, bos=0)
    bind_layers(SourceRoute, IP,          bos=1)

    topo = TopologyParser(topo_path=args.topo_path)
    src  = get_if_addr(args.iface)
    # src  = topo.get_host_addr('h21')         # this line is for testing on normal computer instead of mock ones
    dst  = topo.get_host_addr(args.target)
    print("Send on interface '{}' from {} to {}".format(args.iface, src, dst))

    # define packet format
    pkt = Ether(src=get_if_hwaddr(args.iface), dst='ff:ff:ff:ff:ff:ff')
    ports = topo.get_route_ports(src=src, dst=dst)
    if not len(ports)==0:
        for port in ports:
            pkt = pkt / SourceRoute(bos=0, port=port)
        pkt.getlayer(SourceRoute, len(ports)).bos = 1
    pkt = pkt / IP(dst=dst) / UDP(dport=4321, sport=1234)
    pkt.show2()

    sendp(pkt, iface=args.iface, verbose=False)


if __name__=='__main__':
    main()