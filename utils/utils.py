import networkx as nx

def to_simple_graph(G_multidigraph):
        G_simple = nx.Graph()
        G_simple.add_nodes_from(G_multidigraph.nodes(data=True))

        for u, v, data in G_multidigraph.edges(data=True):
            if not G_simple.has_edge(u, v):
                G_simple.add_edge(u, v, **data)
            else:
                current_grade = G_simple[u][v].get('grade_abs', 0)
                new_grade = data.get('grade_abs', 0)
                if new_grade > current_grade:
                    G_simple[u][v]['grade_abs'] = new_grade
                    G_simple[u][v]['length'] = data.get('length', 0)

        return G_simple