import json
import argparse
from TopologyParser import TopologyParser

def parse_args():
    parser = argparse.ArgumentParser(description='P4 Mininet Runtime Generator')
    parser.add_argument('-T', '--topo-path', type=str, required=True,  metavar='<path>', 
                        help='path to the json topology file')
    args = parser.parse_args()

    return args


def get_runtime_content():
    content = {'target': 'bmv2', 
               'p4info': 'build/source_routing.p4.p4info.txt', 
               'bmv2_json': 'build/source_routing.json', 
               'table_entries': []}
    return content

def main():
    args = parse_args()

    topo = TopologyParser(topo_path=args.topo_path)
    for sw in topo.switches:
        with open(f'topo/{sw}-runtime.json', 'w') as f:
            json.dump(get_runtime_content(), f, indent='\t')
    
    topo.lookup()
    topo.lookup('edge')
        

if __name__=='__main__':
    main()