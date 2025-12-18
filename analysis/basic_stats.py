import osmnx as ox
import networkx as nx
import numpy as np

class NetworkStats:
    
    def __init__(self, G_proj):
        self.G_proj = G_proj
        self.G_simple = nx.Graph(G_proj)
        self.stats = ox.basic_stats(G_proj)
    
    def get_basic_metrics(self) -> dict:
        return {
            'nodes': self.stats['n'],
            'edges': self.stats['m'],
            'intersections': self.stats['intersection_count'],
            'dead_ends': self.stats['n'] - self.stats['intersection_count']
        }
    
    def get_metrics(self) -> dict:
        degrees = [d for n, d in self.G_simple.degree()]
        return {
            'nodes': self.stats['n'],
            'edges': self.stats['m'],
            'avg_degree': np.mean(degrees),
            'avg_clustering': nx.average_clustering(self.G_simple),
            'transitivity': nx.transitivity(self.G_simple),
            'density': nx.density(self.G_simple),
            'diameter_topo': f"{nx.diameter(self.G_simple):.2f}",
            'diameter_meters': f"{nx.diameter(self.G_simple, weight='length'):.2f}"
        }
    
    def get_gcc_info(self) -> dict:
        components = sorted(nx.connected_components(self.G_simple), 
                          key=len, reverse=True)
        gcc_nodes = components[0]
        
        return {
            'gcc_size': len(gcc_nodes),
            'gcc_percentage': (len(gcc_nodes) / len(self.G_simple)) * 100,
            'gcc_nodes': gcc_nodes
        }