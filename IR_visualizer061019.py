import pydotplus
from edg import edgir


def gen_library(file):
	# Generate library by reading in FILE.
	pb = edgir.Library()
	with open(file, "rb") as f:
		pb.ParseFromString(f.read())
	return pb

def gen_visualizer(hierarchy_block, name):
	gen_hblock_graph(file_graph, hierarchy_block, name)
	file_graph.write_png(name + '.png')

def gen_hblock_graph(file_graph, hblock_obj, hblock_name):
	for constraint in hblock_obj.hierarchy_block.constraints:
		if constraint.constraint.HasField('connected'):
			gen_connection_graph(file_graph, hblock_name, constraint.constraint.connected)

def gen_connection_graph(file_graph, hblock_name, connection_obj):
	hblock_port_name = None
	sblock_name = None
	sblock_port_name = None
	link_name = None
	link_port_name = None

	def gen_sub_block_graph(block_port_obj):
		nonlocal hblock_port_name, sblock_name, sblock_port_name

		if len(block_port_obj) == 2:
			sblock_name = block_port_obj[0].local.name
			sblock_port_name = sblock_name + '_' + block_port_obj[1].local.name
			sblock_port_label = block_port_obj[1].local.name

			if not file_graph.get_subgraph('cluster_' + sblock_name):
				sblock_graph = pydotplus.Cluster(graph_name=sblock_name, graph_type='digraph', label=sblock_name)
				file_graph.add_subgraph(sblock_graph)

			sblock_graph = file_graph.get_subgraph('cluster_' + sblock_name)[0]
			if not sblock_graph.get_node(sblock_port_name):
				sblock_port = pydotplus.Node(name=sblock_port_name, label=sblock_port_label, shape='circle')
				sblock_graph.add_node(sblock_port) # Hopefully, this updates the file_graph as well? Yes, seems to.
			
		else:
			hblock_port_name = block_port_obj[0].local.name

	def gen_link_graph(link_port_obj):
		nonlocal link_name, link_port_name

		link_name = link_port_obj[0].local.name
		link_port_name = link_name + '_' + link_port_obj[1].local.name
		link_port_label = link_port_obj[1].local.name

	gen_sub_block_graph(connection_obj.block_port.steps)
	gen_link_graph(connection_obj.link_port.steps)

	print('link name is: ', link_name)
	print('link port name is: ', link_port_name)

	if hblock_port_name:
		connection = pydotplus.Edge(hblock_port_name, link_port_name)
	else:
		connection = pydotplus.Edge(sblock_port_name, link_port_name)

	file_graph.add_edge(connection)


if __name__ == '__main__':
	# Generate library from file
	lib = gen_library("libs.edg")
	file_graph = pydotplus.Dot()

	# Find hierarchy blocks in the library
	for name, elt in lib.root.members.items():

		# If hierarchy block, then generate a visualizer file.
		if elt.HasField('hierarchy_block'):
			for hport_name, _ in elt.hierarchy_block.ports.items():
				hport = pydotplus.Node(name=hport_name, shape='circle')
				file_graph.add_node(hport)
			
			for link_name, _ in elt.hierarchy_block.links.items():
				if not file_graph.get_subgraph('cluster_' + link_name):
					link_graph = pydotplus.Cluster(graph_name=link_name, graph_type='graph', label=link_name)
					source = pydotplus.Node(name=link_name + '_source', label='source', shape='circle')
					sink = pydotplus.Node(name=link_name + '_sinks', label='sinks', shape='circle')
					link_graph.add_node(source)
					link_graph.add_node(sink)
					file_graph.add_subgraph(link_graph)

			gen_visualizer(elt, name)

