TOPO = topo/topology.json
LINK_FILE = examples/links_example
NUM_SWITCHES = 5
NUM_HOSTS = 3

all:
	python3 utils/topo_generator.py -S $(NUM_SWITCHES) -H $(NUM_HOSTS) -l $(LINK_FILE) -T $(TOPO)
	python3 utils/runtime_generator.py -T $(TOPO)

clean:
	find topo/ -type f -name *.json -exec rm {} \;