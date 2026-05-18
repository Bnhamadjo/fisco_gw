from pyvis.network import Network

def visualizar_grafo(G):

    net = Network(height="500px", width="100%", bgcolor="#222", font_color="white")

    for node in G.nodes:
        net.add_node(node, label=node)

    for edge in G.edges:
        net.add_edge(edge[0], edge[1])

    net.save_graph("grafo.html")
    return "grafo.html"