from config.settings import PLACES, MAX_GRADE_NBR9050
from utils.utils import to_simple_graph
from data.network_loader import NetworkLoader
from analysis.basic_stats import NetworkStats
from analysis.centrality import CentralityAnalyzer
from analysis.percolation import PercolationSimulator
from visualization.plots import NetworkVisualizer
import numpy as np

def main():
    
    loader = NetworkLoader()
    # Pipeline completo: download -> segmentação -> elevação
    G_proj, G_seg_elev = loader.load_and_segment_with_elevation(PLACES['botafogo'][0])
    G_simple = to_simple_graph(G_proj)
    G_simple_seg = to_simple_graph(G_seg_elev)

    stats = NetworkStats(G_proj)
    basic_metrics = stats.get_basic_metrics()
    topo_metrics = stats.get_metrics()

    print("\nMétricas Fundamentais:")
    for key, value in basic_metrics.items():
        print(f"  {key}: {value}")

    print("\nMétricas Topológicas:")
    for key, value in topo_metrics.items():
        print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")

    viz = NetworkVisualizer(G_proj)
    viz.plot_basic_network("Rede Pedonal de Botafogo", basic_metrics)
    
    centrality = CentralityAnalyzer(G_proj)

    print("\n[Centrality] Calculando centralidade métrica (weight=length)...")
    bc_metric = centrality.calculate_betweenness(weight='length')
    top_metric = centrality.get_top_nodes(bc_metric)

    print("\n[Centrality] Calculando centralidade topológica (sem peso)...")
    bc_topo = centrality.calculate_betweenness(weight=None, normalized=True, attribute='betweenness_topo')
    top_topo = centrality.get_top_nodes(bc_topo)

    viz.plot_centrality_heatmap(attribute='betweenness', title="Centralidade Métrica (Distância)")
    viz.plot_centrality_heatmap(attribute='betweenness_topo', title="Centralidade Topológica (Estrutura)")
    viz.plot_centrality_divergence(top_metric.items(), top_topo.items())

    percolation = PercolationSimulator(G_simple, G_simple_seg, num_simulations=100)
    fractions = np.linspace(0, 1, 50)
    print("\n" + "="*60)
    print("PERCOLAÇÃO - ARESTAS ALEATORIAS")
    results = percolation.run_simulation(fractions)

    print(f"\n[Resultado] Limiar Crítico: {results['critical_threshold']:.4f}")
    viz.plot_percolation_results(results, title="Percolação Aleatória - Robustez da Rede")

    print("\n" + "="*60)
    print("PERCOLAÇÃO DIRECIONADA - ARESTAS INACESSÍVEIS")
    print("="*60)
    results_targeted = percolation.run_targeted_percolation(max_grade_threshold=MAX_GRADE_NBR9050)

    print(f"\n[Resultado] Arestas inacessíveis: {results_targeted['num_inaccessible']}")
    print(f"[Resultado] Porcentagem da rede: {results_targeted['pct_inaccessible']:.2f}%")
    print(f"[Resultado] Limiar crítico: {results_targeted['critical_threshold']:.4f}")

    viz.plot_percolation_results(
        results_targeted,
        title=f"Percolação Direcionada - Remoção de Ladeiras (>{MAX_GRADE_NBR9050*100:.1f}%)"
    )

    if results_targeted['num_inaccessible'] > 0:
        if results_targeted['g2_sizes'] and len(results_targeted['g2_sizes']) > 0:
            idx_critical = int(np.argmax(results_targeted['g2_sizes']))
        else:
            idx_critical = 0
        f_critical = results_targeted['fractions'][idx_critical]

        print(f"[Resultado] Limiar crítico (remoção de inacessíveis): {f_critical:.4f}")

        viz.plot_percolation_results(
            {
                'fractions': results_targeted['fractions'],
                'avg_G1': results_targeted['g1_sizes'],
                'avg_G2': results_targeted['g2_sizes'],
                'critical_threshold': f_critical,
                'max_G2': results_targeted['g2_sizes'][idx_critical]
            },
            title=f"Percolação Direcionada - Remoção de Ladeiras (>{MAX_GRADE_NBR9050*100:.1f}%)"
        )

    print("\n" + "="*60)
    print("ANÁLISE CONCLUÍDA")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
