import osmnx as ox 
import networkx as nx

def get_area(postal_code, city, country):

    return ox.geocode_to_gdf(f"{postal_code}, {city}, {country}")

def get_nodes_edges(area):

    polygon = area.geometry.iloc[0]
    G = ox.graph_from_polygon(polygon, network_type="bike")

    print("Number of Nodes:", G.number_of_nodes())
    print("Number of Edge:", G.number_of_edges())

    return G

def plot_map(G):

    ox.plot_graph(G)

def find_route(G, start_node, end_node):

    return nx.shortest_path(G, source=start_node, target=end_node, weight="length")

def plot_route(G, route):

    return ox.plot_graph_route(G, route, route_color="red", node_size=0)

def route_edges(G, route):

    return ox.routing.route_to_gdf(G, route, weight="length")

def calculate_travel_minutes(distance_m, speed_kmh):
    m_to_km = distance_m/1000

    return (m_to_km / speed_kmh)*60

if __name__ == "__main__":

    area = get_area("10245", "Berlin", "Germany")
    G = get_nodes_edges(area)
    plot_map(G) 
    nodes = list(G.nodes)
    start_node = nodes[123]
    end_node = nodes[234] 
    route = find_route(G, start_node, end_node)
    plot_route(G, route)
    edges = route_edges(G, route)
    distance_m = edges["length"].sum()
    travel_time = calculate_travel_minutes(distance_m, 15)

    print(f"Travel Time: {travel_time:.1f} min")
