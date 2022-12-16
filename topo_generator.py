import json
import argparse

class Topology:
    def __init__(self, num_switch, num_host):
        self.num_switch   = num_switch
        self.num_host     = num_host

        self.get_switches()
        self.get_hosts()
        self.get_links()
    
    def get_switches(self):
        switches = dict()
        for swid in range(1, self.num_switch + 1):
            switches[f's{swid}'] = {'runtime_json': f'topo/s{swid}-runtime.json'}
        self.switches = switches
    
    def get_hosts(self):
        hosts = dict()
        for swid in range(1, self.num_switch + 1):
            for hid in range(1, self.num_host + 1):
                # IP: available ip postfix [2, 4, ..., 252]
                # GW: following gateway postfix [3, 5, ..., 253]
                ip_postfix = hid * 2
                hosts[f'h{swid}{hid}'] = {'ip':       f'10.0.{swid}.{ip_postfix}/31', 
                                          'mac':      f'08:00:00:00:0{swid}:0{hid}', 
                                          'commands': [f'route add default gw 10.0.{swid}.{ip_postfix + 1} dev eth0', 
                                                       f'arp -i eth0 -s 10.0.{swid}.{ip_postfix + 1} 08:00:00:00:0{swid}:00']}
        self.hosts = hosts

    def get_links(self):
        # link between hosts and switches must be in the form `hX-sX`
        # this rule is written in tutorial/utils/run_exercise.py
        links = list()
        for swid in range(1, self.num_switch + 1):
            for hid in range(1, self.num_host + 1):
                links.append([f'h{swid}{hid}', f's{swid}-p{hid}'])
        self.links = links
        
    def append_links(self, append_links):
        available_ports = {s: self.num_host + 1 for s in self.switches}
        new_links = list()
        for links in append_links.split(','):
            s_first, s_second = links.split('-')
            conn = [f'{s_first}-p{available_ports[s_first]}', f'{s_second}-p{available_ports[s_second]}']
            available_ports[s_first] += 1
            available_ports[s_second] += 1
            new_links.append(conn)
        self.links += new_links
    
    def dump(self, json_path=None):
        output = {'hosts': self.hosts, 'switches': self.switches, 'links': self.links}
        if json_path is None:
            print(json.dumps(output, indent=4))
        else:
            with open(json_path, 'w') as f:
                json.dump(output, f, indent='\t')


def parse_args():
    parser = argparse.ArgumentParser(description='P4 Mininet Topology Generator')
    parser.add_argument('-S', '--num-switch', type=int, required=True,  metavar='N', 
                        help='Number of switches in your topology (Max: 9)')
    parser.add_argument('-H', '--num-host',   type=int, required=True,  metavar='N', 
                        help='Number of hosts behide every switch (Max: 5)')
    parser.add_argument('-L', '--links',      type=str, required=False, metavar='s1-s2,s1-s3', 
                        help='Links between every two switches separated by comma')
    parser.add_argument('-l', '--links-file', type=str, required=False, metavar='FILE', 
                        help='Links between every two switches separated by comma')
    parser.add_argument('-t', '--topo-path',  type=str, required=False, metavar='FILE', 
                        help='Path to save the topology')
    args = parser.parse_args()

    assert args.num_switch<=9, "Maximum number of switches: 9"
    assert args.num_host<=5,   "Maximum number of hosts: 5"
    if args.links is not None:
        args.switch_links = args.links
    elif args.links_file is not None:
        with open(args.links_file, 'r') as f:
            args.switch_links = f.readline()
    else:
        raise Exception('Both `--links` and `--links-file` are not defined')
    
    return args
    

def main():
    args = parse_args()

    topo = Topology(args.num_switch, args.num_host)
    topo.append_links(args.switch_links)
    topo.dump(json_path=args.topo_path)


if __name__=='__main__':
    main()