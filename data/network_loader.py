import osmnx as ox
import networkx as nx
import math
from shapely.geometry import LineString
from config.settings import (
    OSMNX_CACHE, OSMNX_LOG, NETWORK_TYPE, 
    GOOGLE_ELEVATION_API_KEY, GOOGLE_ELEVATION_PAUSE, SEGMENT_LENGTH
)

class NetworkLoader:
    def __init__(self):
        ox.settings.use_cache = OSMNX_CACHE
        ox.settings.log_console = OSMNX_LOG

    def load_network(self, place_name: str, simplify: bool = True):
        print(f"[Data] Baixando rede de {place_name}...")
        G = ox.graph_from_place(place_name, network_type=NETWORK_TYPE, simplify=simplify)
        G_proj = ox.project_graph(G)
        return G_proj

    def segment_graph(self, G_proj, segment_length=SEGMENT_LENGTH):
        print(f"[Data] Segmentando arestas maiores que {segment_length} m...")
        Gs = nx.MultiDiGraph()
        Gs.graph.update(G_proj.graph)
        Gs.add_nodes_from(G_proj.nodes(data=True))

        next_virtual_id = -1

        for u, v, k, data in G_proj.edges(keys=True, data=True):
            geom = data.get("geometry")
            if geom is None:
                p1 = G_proj.nodes[u]
                p2 = G_proj.nodes[v]
                geom = LineString([(p1['x'], p1['y']), (p2['x'], p2['y'])])

            total_len = float(data.get("length", geom.length))

            if total_len <= segment_length * 1.05:
                Gs.add_edge(u, v, key=k, **dict(data))
                continue

            n_segs = max(1, int(math.ceil(total_len / segment_length)))
            cut_ds = [i * (total_len / n_segs) for i in range(n_segs + 1)]

            prev_node = u
            prev_pt = geom.interpolate(cut_ds[0])

            for i in range(1, len(cut_ds)):
                pt = geom.interpolate(cut_ds[i])

                if i == len(cut_ds) - 1:
                    curr_node = v
                else:
                    curr_node = next_virtual_id
                    next_virtual_id -= 1
                    Gs.add_node(curr_node, x=float(pt.x), y=float(pt.y), virtual=True)

                seg_geom = LineString([(prev_pt.x, prev_pt.y), (pt.x, pt.y)])
                seg_data = dict(data)
                seg_data["geometry"] = seg_geom
                seg_data["length"] = float(seg_geom.length)
                seg_data["orig_edge_key"] = k

                new_key = f"{k}_{i-1}"
                Gs.add_edge(prev_node, curr_node, key=new_key, **seg_data)
                prev_node = curr_node
                prev_pt = pt

        print(f"[Data] Segmentação concluída: {Gs.number_of_nodes()} nós, {Gs.number_of_edges()} arestas")
        return Gs

    def add_elevation_data(self, G_proj, api_key=None):
        if api_key is None:
            api_key = GOOGLE_ELEVATION_API_KEY

        if not api_key:
            print("[Data] AVISO: Sem chave de API. Pulando elevação (grade=0).")
            nx.set_edge_attributes(G_proj, 0, "grade_abs")
            return G_proj

        print("[Data] Consultando Google Elevation API...")
        G_ll = ox.project_graph(G_proj, to_crs="EPSG:4326")

        try:
            G_ll = ox.elevation.add_node_elevations_google(
                G_ll, api_key=api_key, pause=GOOGLE_ELEVATION_PAUSE
            )
            G_ll = ox.elevation.add_edge_grades(G_ll, add_absolute=True)
            G_final = ox.project_graph(G_ll)
            print("[Data] Elevação adicionada com sucesso!")
            return G_final
        except Exception as e:
            nx.set_edge_attributes(G_proj, 0, "grade_abs")
            return G_proj

    def load_and_segment_with_elevation(self, place_name: str):
        G_proj = self.load_network(place_name)

        G_seg = self.segment_graph(G_proj)

        G_seg_elev = self.add_elevation_data(G_seg)

        return G_proj, G_seg_elev

