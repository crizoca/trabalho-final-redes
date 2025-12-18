import numpy as np
import networkx as nx
from tqdm import tqdm

class PercolationSimulator:
    def __init__(self, G_simple, G_simple_segmented=None, num_simulations=100):
        self.G_lcc = self._extract_lcc(G_simple)
        self.N_lcc = self.G_lcc.number_of_nodes()
        self.M_lcc = self.G_lcc.number_of_edges()
        
        if G_simple_segmented is not None:
            self.G_lcc_seg = self._extract_lcc(G_simple_segmented)
            self.N_seg = self.G_lcc_seg.number_of_nodes()
            self.M_seg = self.G_lcc_seg.number_of_edges()
        else:
            self.G_lcc_seg = None
            self.N_seg = 0
            self.M_seg = 0
        
        self.num_simulations = num_simulations
        
        print(f"[Percolation] LCC original: N={self.N_lcc}, E={self.M_lcc}")
        if self.G_lcc_seg:
            print(f"[Percolation] LCC segmentado: N={self.N_seg}, E={self.M_seg}")
    
    def _extract_lcc(self, G):
        if G.is_directed():
            G_u = G.to_undirected()
        else:
            G_u = G.copy()
        
        comps = sorted(nx.connected_components(G_u), key=len, reverse=True)
        if not comps:
            raise ValueError("Grafo vazio ou sem componentes conectados.")
        
        return G_u.subgraph(comps[0]).copy()
    
    def run_simulation(self, fractions: np.ndarray) -> dict:
        print(f"[Percolation] Simulando percolação aleatória (N={self.N_lcc}, E={self.M_lcc})...")
        results_G1 = {f: [] for f in fractions}
        results_G2 = {f: [] for f in fractions}
        
        for f in tqdm(fractions, desc="Simulando"):
            num_edges_to_remove = int(self.M_lcc * f)
            
            for _ in range(self.num_simulations):
                g1, g2 = self._simulate_removal(num_edges_to_remove)
                results_G1[f].append(g1)
                results_G2[f].append(g2)
        
        return self._process_results(fractions, results_G1, results_G2)
    
    def _simulate_removal(self, num_edges: int) -> tuple:
        H = self.G_lcc.copy()
        
        if num_edges > 0:
            edges = list(H.edges())
            num_edges = min(num_edges, len(edges))
            if num_edges > 0:
                indices = np.random.choice(len(edges), num_edges, replace=False)
                H.remove_edges_from([edges[i] for i in indices])
        
        comps = sorted(nx.connected_components(H), key=len, reverse=True)
        
        g1 = len(comps[0]) / self.N_lcc if comps else 0.0
        g2 = len(comps[1]) / self.N_lcc if len(comps) > 1 else 0.0
        
        return g1, g2
    
    def _process_results(self, fractions, results_G1, results_G2) -> dict:
        avg_G1 = [np.mean(results_G1[f]) for f in fractions]
        avg_G2 = [np.mean(results_G2[f]) for f in fractions]
        
        idx_critical = int(np.argmax(avg_G2))
        
        return {
            'fractions': fractions,
            'avg_G1': avg_G1,
            'avg_G2': avg_G2,
            'critical_threshold': fractions[idx_critical],
            'max_G2': avg_G2[idx_critical]
        }
    
    def run_targeted_percolation(self, max_grade_threshold=0.0833):
        if self.G_lcc_seg is None:
            raise ValueError("Grafo segmentado não foi fornecido no __init__.")
        
        print(f"[Percolation] Percolação direcionada: removendo APENAS arestas inacessíveis (grade > {max_grade_threshold*100:.2f}%)")
        
        inaccessible_edges = [
            (u, v, d.get('grade_abs', 0)) 
            for u, v, d in self.G_lcc_seg.edges(data=True)
            if d.get('grade_abs', 0) > max_grade_threshold
        ]
        
        num_inaccessible = len(inaccessible_edges)
        pct_inaccessible = (num_inaccessible / self.M_seg) * 100 if self.M_seg > 0 else 0
        
        print(f"[Percolation] Total de arestas: {self.M_seg}")
        print(f"[Percolation] Arestas inacessíveis: {num_inaccessible} ({pct_inaccessible:.2f}%)")
        
        if num_inaccessible == 0:
            print("[Percolation] AVISO: Nenhuma aresta inacessível encontrada!")
            return {
                'fractions': [0],
                'avg_G1': [1.0],
                'avg_G2': [0.0],
                'num_inaccessible': 0,
                'pct_inaccessible': 0
            }
        
        inaccessible_edges_sorted = sorted(inaccessible_edges, key=lambda x: x[2], reverse=True)
        edges_to_remove = [(u, v) for u, v, _ in inaccessible_edges_sorted]
        
        max_fraction = num_inaccessible / self.M_seg  
        fractions = np.linspace(0, max_fraction, 50)
        
        results_G1 = []
        results_G2 = []
        
        for f in tqdm(fractions, desc="Removendo inacessíveis"):
            num_to_remove = int(self.M_seg * f)
            num_to_remove = min(num_to_remove, num_inaccessible)  
            
            H = self.G_lcc_seg.copy()
            
            if num_to_remove > 0:
                H.remove_edges_from(edges_to_remove[:num_to_remove])
            
            comps = sorted(nx.connected_components(H), key=len, reverse=True)
            
            g1 = len(comps[0]) / self.N_seg if comps else 0.0
            g2 = len(comps[1]) / self.N_seg if len(comps) > 1 else 0.0
            
            results_G1.append(g1)
            results_G2.append(g2)
        
        idx_critical = int(np.argmax(results_G2))
        
        return {
            'fractions': fractions,
            'avg_G1': results_G1,
            'avg_G2': results_G2,
            'critical_threshold': fractions[idx_critical],
            'max_G2': results_G2[idx_critical],
            'num_inaccessible': num_inaccessible,
            'pct_inaccessible': pct_inaccessible
        }