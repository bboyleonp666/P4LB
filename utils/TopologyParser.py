import re
import json

class TopologyParser:
    def __init__(self, topo_path):
        self.topo_path = topo_path
        self.parse(topo_path)

    def parse(self, topo_path):
        with open(topo_path, 'r') as f:
            topo = json.load(f)
        self.hNames = [host for host in topo['hosts']]
        self.hIps   = [topo['hosts'][host]['ip'].split('/')[0] for host in topo['hosts']]
        self.hMacs  = [topo['hosts'][host]['mac'] for host in topo['hosts']]

        switches = list(topo['switches'].keys())
        edges = {key: [key] for key in switches}
        fwd_ports = {key: dict() for key in switches}
        for l in topo['links']:
            if not l[0][0]=='h':
                s1, p1 = l[0].split('-')
                s2, p2 = l[1].split('-')
                edges[s1].append(s2)
                edges[s2].append(s1)
                fwd_ports[s1][s2] = int(p1[1:])
                fwd_ports[s2][s1] = int(p2[1:])

        self.switches  = switches
        self.edges     = edges
        self.fwd_ports = fwd_ports
        self.Floyd_Warshall()

    def Floyd_Warshall(self):
        """
        Floyd Warshall all pairs shortest paths algorithm with equal weights
        """
        switches = self.switches
        edges    = self.edges
        
        MAX = len(switches) + 1
        dists = {sw1 : {sw : MAX for sw in switches} for sw1 in switches}
        paths = {sw1 : {sw : list() for sw in switches} for sw1 in switches}

        for s, dst in edges.items():
            for d in dst:
                if not s==d:
                    dists[s][d] = 1
                    paths[s][d] = [s, d]

                else:
                    dists[s][d] = 0
                    paths[s][d] = [s]
            
        for via in switches:
            for s in switches:
                for d in switches:
                    if s==d or s==via or d==via or dists[s][d]<=1:
                        continue
                    
                    if len(paths[s][via])>0 and len(paths[via][d])>0 and (dists[s][via] + 1)<dists[s][d]:
                        paths[s][d] = paths[s][via] + paths[via][d][1:]
                        dists[s][d] = dists[s][via] + 1
        
        self.dists = dists
        self.paths = paths

    def get_route_ports(self, src, dst):
        src = self.get_host_addr(src)
        dst = self.get_host_addr(dst)
        assert src!=dst, "Source should not be the same as Destination"
        
        src_sw = self.get_proxy_switch(src)
        dst_sw = self.get_proxy_switch(dst)

        s2h_port = [int(dst.split('.')[-1]) // 2]
        if src_sw==dst_sw:
            return s2h_port
        
        else:
            path = self.paths[src_sw][dst_sw]
            ports = [self.fwd_ports[path[i]][path[i+1]] for i in range(len(path) - 1)]
            return ports + s2h_port

    def lookup(self, mode='node'):
        if mode=='node':
            print('Nodes')
            print('----------')
            for sw in self.switches:
                print(f'{sw} : {self.fwd_ports[sw]}')
            print()

        elif mode=='edge':
            print('Edges')
            print('----------')
            for sw in self.switches:
                print(f'{sw} : {self.edges[sw]}')
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