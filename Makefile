TOPO = topo/topology.json
LINK_FILE = examples/links_example
NUM_SWITCHES = 5
NUM_HOSTS = 3

all:
	python topo_generator.py -S $(NUM_SWITCHES) -H $(NUM_HOSTS) -l $(LINK_FILE) -t $(TOPO)

clean:
	rm $(TOPO)
