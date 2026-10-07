import json
import statistics
from pathlib import Path
from typing import Any

import networkx as nx
from networkx import Graph

from iglink.common.graph_loader import Community, GraphLoader, mutuals_of


class StatsCreator:
    TOP_AMOUNT = 10

    def __init__(self, graph_loader: GraphLoader):
        self.graph_loader = graph_loader

    def create_stats(
            self,
            followers_file: Path,
            mutuals_file: Path,
            stats_file: Path,
            colors: list[str],
            community_seed: int,
            community_resolution: float,
            exclude_follower_names,
            community_labels: dict[int, str],
    ):
        graph = self.graph_loader.load_graph(followers_file, mutuals_file, exclude_follower_names)
        communities = self.graph_loader.detect_communities(
            graph, colors, community_seed, community_resolution, community_labels)

        stats = self.calculate_stats(graph, communities)

        with open(stats_file, 'w', encoding='utf-8') as fd:
            json.dump(stats, fd, indent=2, ensure_ascii=False)

        self._print_stats(stats)
        print(f"\nSaved statistics to {stats_file}")

    def calculate_stats(self, graph: Graph, communities: list[Community]) -> dict[str, Any]:
        community_map = {person_id: community for community in communities for person_id in community.members}
        connections = dict(graph.degree())
        mutuals = {node: mutuals_of(graph, node) for node in graph.nodes()}
        cross_connections = {
            node: sum(1 for neighbor in graph[node] if community_map[neighbor].id != community_map[node].id)
            for node in graph.nodes()
        }
        cross_amount = sum(cross_connections.values()) // 2
        amounts = list(mutuals.values()) or [0]

        def person(node) -> dict[str, Any]:
            return {
                'username': graph.nodes[node].get('username', 'unknown'),
                'mutuals': mutuals[node],
                'connections': connections[node],
                'cross_community_connections': cross_connections[node],
                'community': community_map[node].name,
            }

        def top(ranking: dict) -> list[dict[str, Any]]:
            ranked = sorted(ranking, key=lambda node: (-ranking[node], graph.nodes[node].get('username', '')))
            return [person(node) for node in ranked[:self.TOP_AMOUNT] if ranking[node] > 0]

        community_stats = []
        for community in communities:
            if community.is_small:
                continue
            inside = graph.subgraph(community.members).number_of_edges()
            outside = sum(cross_connections[node] for node in community.members)
            most_mutuals = max(community.members, key=lambda node: (mutuals[node], connections[node]))
            community_stats.append({
                'id': community.id,
                'name': community.name,
                'color': community.color,
                'people': community.size,
                'connections_inside': inside,
                'connections_to_other_communities': outside,
                'most_mutuals': graph.nodes[most_mutuals].get('username', 'unknown'),
            })

        small_communities = [community for community in communities if community.is_small]
        components = [len(component) for component in nx.connected_components(graph)]

        return {
            'people': graph.number_of_nodes(),
            'connections': graph.number_of_edges(),
            'isolated_people': sum(1 for amount in connections.values() if amount == 0),
            'mutuals_per_person': {
                'mean': round(statistics.mean(amounts), 2),
                'median': statistics.median(amounts),
                'max': max(amounts),
            },
            'density': round(nx.density(graph), 4),
            'average_clustering': round(nx.average_clustering(graph), 4) if graph.number_of_nodes() > 0 else 0,
            'largest_connected_group': max(components, default=0),
            'cross_community_connections': cross_amount,
            'cross_community_share': round(cross_amount / graph.number_of_edges(), 4) if cross_amount else 0,
            'communities': community_stats,
            'people_without_community': sum(community.size for community in small_communities),
            'most_mutuals': top(mutuals),
            'most_cross_community_connections': top(cross_connections),
        }

    def _print_stats(self, stats: dict[str, Any]):
        per_person = stats['mutuals_per_person']

        print("\n=== Overview ===")
        rows = [
            ("People", stats['people']),
            ("Connections", stats['connections']),
            ("Isolated people (no connection)", stats['isolated_people']),
            ("Mutuals per person (mean)", per_person['mean']),
            ("Mutuals per person (median)", per_person['median']),
            ("Mutuals per person (max)", per_person['max']),
            ("Density", stats['density']),
            ("Average clustering", stats['average_clustering']),
            ("Largest connected group", stats['largest_connected_group']),
            ("Cross-community connections",
             f"{stats['cross_community_connections']} ({stats['cross_community_share']:.1%})"),
            ("People without community", stats['people_without_community']),
        ]
        for name, value in rows:
            print(f"{name:<34}{value:>12}")

        print("\n=== Communities ===")
        print(f"{'Name':<24}{'People':>8}{'Inside':>8}{'Outside':>9}  Most mutuals")
        for community in stats['communities']:
            print(
                f"{community['name']:<24}"
                f"{community['people']:>8}"
                f"{community['connections_inside']:>8}"
                f"{community['connections_to_other_communities']:>9}"
                f"  {community['most_mutuals']}"
            )

        print("\n=== Most mutuals ===")
        for rank, person in enumerate(stats['most_mutuals'], start=1):
            print(f"{rank:>2}. {person['username']:<30}{person['mutuals']:>5}  {person['community']}")

        print("\n=== Most cross-community connections ===")
        for rank, person in enumerate(stats['most_cross_community_connections'], start=1):
            print(f"{rank:>2}. {person['username']:<30}{person['cross_community_connections']:>5}"
                  f" of {person['connections']:<5}{person['community']}")
