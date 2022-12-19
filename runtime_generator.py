import json
import argparse
import networkx as nx
import re

class TopologyParser:
    def __init__(self, topo_path):
        self.topo_path = topo_path

        self.parse(topo_path)
        self.compute_shortest_paths()

    def parse(self, topo_path):
        with open(topo_path, 'r') as f:
            topo = json.load(f)
        self.hNames = [host for host in topo['hosts']]
        self.hIps   = [topo['hosts'][host]['ip'].split('/')[0] for host in topo['hosts']]
        self.hMacs  = [topo['hosts'][host]['mac'] for host in topo['hosts']]

        switch_attrs = {key: dict() for key in topo['switches'].keys()}
        edge_attrs = list()
        for l in topo['links']:
            if not l[0][0]=='h':
                s1, p1 = l[0].split('-')
                s2, p2 = l[1].split('-')
                switch_attrs[s1][s2] = int(p1[1:])
                switch_attrs[s2][s1] = int(p2[1:])
                edge_attrs.append((s1, s2))
        node_attrs = [(key, val) for key, val in switch_attrs.items()]

        G = nx.Graph()
        G.add_nodes_from(node_attrs)
        G.add_edges_from(edge_attrs)
        self.topo = G

    def compute_shortest_paths(self, cutoff=None):
        paths = nx.all_pairs_shortest_path(self.topo, cutoff=cutoff)
        self.paths = dict(paths)

    def get_route_ports(self, src, dst):
        src = self.get_host_addr(src)
        dst = self.get_host_addr(dst)
        assert src!=dst, "Source should not be the same as Destination"
        
        src_sw = self.get_proxy_switch(src)
        dst_sw = self.get_proxy_switch(dst)
        if src_sw==dst_sw:
            # return [int(dst.split('.')[-1]) // 2]
            return []
        
        else:
            path = self.paths[src_sw][dst_sw]
            topo = self.topo.nodes
            ports = [topo[path[i]][path[i+1]] for i, _ in enumerate(path[:-1])]
            return ports

    def lookup(self, mode='node'):
        if mode=='node':
            print('Nodes')
            print('----------')
            for node in self.topo.nodes:
                print(f'{node} : {self.topo.nodes[node]}')
            print()

        elif mode=='edge':
            print('Edges')
            print('----------')
            print(self.topo.edges)
            print()
            
    def get_host_addr(self, host):
        assert host[0]!='s', "The input should be host name or IPv4 address, not switch name"
        if '.' in host:
            self.check_ipv4(host)
            return host

        assert host in self.hNames, f"The target '{host}' is not in the topology"
        return self.hIps[self.hNames.index(host)]
    
    def get_host_name(self, host):
        assert host[0]!='s', "The input should be host name or IPv4 address, not switch name"
        if host[0]=='h':
            assert host in self.hNames, f"The target '{host}' is not in the topology"
            return host
            
        self.check_ipv4(host)
        assert host in self.hIps, f"The target '{host}' is not in the topology"
        return self.hNames[self.hIps.index(host)]
    
    def get_proxy_switch(self, host):
        addr = self.get_host_addr(host)
        idx = addr.split('.')[-2]
        return f's{idx}'
    
    def check_ipv4(self, addr):
        pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
        assert re.match(pattern=pattern, string=addr) is not None, f"'{addr}' is not a valid IPv4 address"

            
def parse_args():
    parser = argparse.ArgumentParser(description='P4 Mininet Runtime Generator')
    parser.add_argument('-T', '--topo-path', type=str, required=True,  metavar='<path>', 
                        help='path to the json topology file')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    topo_parser = TopologyParser(topo_path=args.topo_path)
    topo_parser.lookup(mode='node')
    topo_parser.lookup(mode='edge')

    ports = topo_parser.get_route_ports(src='h41', dst='h53')
    print(ports)


if __name__=='__main__':
    main()