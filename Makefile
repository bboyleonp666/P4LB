BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = topo/topology.json

LINK_FILE = examples/links_example
NUM_SWITCHES = 5
NUM_HOSTS = 3

include ../../utils/Makefile

.PHONY: myrun topo myclean

myrun: topo run

topo:
	python3 utils/topo_generator.py -S $(NUM_SWITCHES) -H $(NUM_HOSTS) -l $(LINK_FILE) -T $(TOPO)
	python3 utils/runtime_generator.py -T $(TOPO)

myclean: clean
	find topo/ -type f -name *.json -exec rm {} \;