#!/usr/bin/env python3

import sys

from scapy.all import Ether, IPOption, Packet, bind_layers, sniff
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR

IPV4_TYPE = 0x800

class IPOption_MRI(IPOption):
    name = 'MRI'
    option = 31
    fields_desc = [_IPOption_HDR, 
                   FieldLenField('length', None, fmt='B', length_of='swids', adjust=lambda l : l+4), 
                   ShortField('count', 0), 
                   FieldListField('swids', [], IntField('', 0), length_from=lambda pkt : pkt.count * 4)]


def handle_pkt(pkt):
    print('Got packet!')
    pkt.show2()
    sys.stdout.flush()
    

class SourceRoute(Packet):
    fields_desc = [BitField('bos',  0,  1), 
                   BitField('port', 0, 15)]
    
class SourceRoutingTail(Packet):
    fields_desc = [XShortField('etherType', IPV4_TYPE)]


def main():
    iface = 'eth0'

    bind_layers(Ether,       SourceRoute,       type=0x1234)
    bind_layers(SourceRoute, SourceRoute,       bos=0)
    bind_layers(SourceRoute, SourceRoutingTail, bos=1)

    print(f'Sniffing on {iface}')
    sys.stdout.flush()
    sniff(filter='udp and port 4321', 
          iface=iface, 
          prn=lambda x : handle_pkt(x))


if __name__=='__main__':
    main()