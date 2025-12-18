import networkx as nx
import pandas as pd

class CentralityAnalyzer:
    
    def __init__(self, G_proj):
        self.G_proj = G_proj
    
    def calculate_betweenness(self, weight='length', normalized=True, attribute='betweenness') -> dict:
        bc = nx.betweenness_centrality(self.G_proj, weight=weight, normalized=normalized)
        nx.set_node_attributes(self.G_proj, bc, attribute)
        return bc
    
    def get_top_nodes(self, centrality_dict: dict, n: int = 5) -> pd.Series:
        return pd.Series(centrality_dict).sort_values(ascending=False).head(n)
    
    def get_node_info(self, node_id) -> dict:
        node_data = self.G_proj.nodes[node_id]
        return {
            'id': node_id,
            'lat': node_data.get('y'),
            'lon': node_data.get('x')
        }