import matplotlib.pyplot as plt
import osmnx as ox
from config.settings import *

class NetworkVisualizer:
    def __init__(self, G_proj):
        self.G_proj = G_proj
    
    def plot_basic_network(self, title: str, stats: dict = None):
        fig, ax = ox.plot_graph(
            self.G_proj,
            node_size=DEFAULT_NODE_SIZE,
            edge_color=DEFAULT_EDGE_COLOR,
            edge_linewidth=DEFAULT_EDGE_WIDTH,
            bgcolor=BACKGROUND_COLOR,
            show=False
        )
        
        if stats:
            info_text = f"Nós: {stats['nodes']}\nArestas: {stats['edges']}"
            ax.text(0.95, 0.05, info_text, transform=ax.transAxes,
                   ha='right', va='bottom', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white'))
        
        plt.title(title)
        plt.show()
    
    def plot_centrality_heatmap(self, attribute='betweenness', cmap='plasma', title="Mapa de Centralidade"):
        nc = ox.plot.get_node_colors_by_attr(self.G_proj, attribute, cmap=cmap)
        
        fig, ax = ox.plot_graph(
            self.G_proj,
            node_color=nc,
            node_size=30,
            edge_color='#333333',
            edge_linewidth=0.5,
            bgcolor=BACKGROUND_COLOR,
            show=False
        )
        
        values = [self.G_proj.nodes[n].get(attribute, 0) for n in self.G_proj.nodes()]
        sm = plt.cm.ScalarMappable(cmap=cmap, 
                                   norm=plt.Normalize(vmin=min(values), vmax=max(values)))
        sm._A = []
        cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label(f'{attribute.capitalize()}')
        
        plt.title(title)
        plt.show()
    
    def plot_percolation_results(self, results: dict, title = "Remoção de Arestas Aleatórias"):
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # G1
        ax1.plot(results['fractions'], results['avg_G1'], 
                color='tab:blue', linewidth=2, label='G1')
        ax1.set_xlabel('Fração Removida (f)')
        ax1.set_ylabel('G1/N', color='tab:blue')
        ax1.grid(True, alpha=0.3)
        
        # G2
        ax2 = ax1.twinx()
        ax2.plot(results['fractions'], results['avg_G2'], 
                color='tab:red', linewidth=2, linestyle='--', label='G2')
        ax2.set_ylabel('G2/N', color='tab:red')
        
        # Limiar crítico
        plt.axvline(x=results['critical_threshold'], color='green', 
                   linestyle=':', label=f"f*={results['critical_threshold']:.2f}")
        
        plt.title("Análise de Percolação")
        plt.tight_layout()
        plt.show()
        
    def plot_centrality_divergence(self, top_topo, top_metric):
        node_colors = ['#dddddd' for _ in self.G_proj.nodes()]
        node_sizes = [10 for _ in self.G_proj.nodes()]
        node_to_idx = {node: i for i, node in enumerate(self.G_proj.nodes())}

        for node, _ in top_topo:
            if node in node_to_idx:
                idx = node_to_idx[node]
                node_colors[idx] = 'blue'
                node_sizes[idx] = 100

        for node, _ in top_metric:
            if node in node_to_idx:
                idx = node_to_idx[node]
                node_colors[idx] = 'red'
                node_sizes[idx] = 100

        fig, ax = ox.plot_graph(self.G_proj, node_color=node_colors, node_size=node_sizes,
                                edge_color='#999999', edge_linewidth=0.5,
                                bgcolor='white', show=False)
        
        ax.text(0.05, 0.95, "AZUL: Topológico (Estrutura)\nVERMELHO: Métrico (Distância)", 
                transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='white'))
        plt.title("Divergência de Centralidade")
        plt.show()