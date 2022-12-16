import json
import argparse
import networkx as nx


class TopologyParser:
    def __init__(self, topo_path):
        self.topo_path = topo_path

        self.parse(topo_path)
        self.compute_shortest_paths()

    def parse(self, topo_path):
        with open(topo_path, 'r') as f:
            topo = json.load(f)

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

    def get_route_ports(self, src, tgt):
        assert src!=tgt, "Source should not be the same as Target"
        path = self.paths[src][tgt]

        ports = list()
        for i, sw in enumerate(path[:-1]):
            ports.append(self.topo.nodes[path[i]][path[i + 1]])
        
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


def parse_args():
    parser = argparse.ArgumentParser(description='P4 Mininet Runtime Generator')
    parser.add_argument('-t', '--topo-path', type=str, required=True,  metavar='<path>', 
                        help='path to the json topology file')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    topo_parser = TopologyParser(topo_path=args.topo_path)
    topo_parser.lookup(mode='node')
    topo_parser.lookup(mode='edge')

    ports = topo_parser.get_route_ports(src='s4', tgt='s5')
    print(f's4 -> s5 : {ports}')
    ports = topo_parser.get_route_ports(src='s1', tgt='s2')
    print(f's1 -> s2 : {ports}')

if __name__=='__main__':
    main()