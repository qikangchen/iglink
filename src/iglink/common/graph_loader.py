import itertools
from dataclasses import dataclass
from pathlib import Path

import jsonlines
import networkx as nx
import pandas as pd
from networkx import Graph
from networkx.algorithms.community.louvain import louvain_communities


@dataclass(frozen=True)
class Community:
    SMALL_MAX_SIZE = 3
    SMALL_COLOR = '#B2BEB5'

    id: int
    members: frozenset
    color: str
    label: str

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def is_small(self) -> bool:
        return self.size <= self.SMALL_MAX_SIZE

    @property
    def name(self) -> str:
        return self.label or f"Community #{self.id}"


def mutuals_of(graph: Graph, node) -> int:
    """How many mutuals instagram lists for a person.

    This is not always the same as the connections in the graph (graph.degree): instagram only lists the people
    *you follow* who follow this person. So anna can be in the list of ben without ben being in the list of anna.
    The graph connects both, the mutuals are only the list of the person itself.
    """
    return graph.nodes[node].get('mutuals', 0)


class GraphLoader:

    def load_graph(self, followers_file: Path, mutuals_file: Path, exclude_follower_names) -> Graph:
        df_followers = self._read_followers(followers_file, exclude_follower_names)
        df_mutuals = self._read_mutuals(mutuals_file, df_followers)
        return self._create_graph(df_mutuals)

    def detect_communities(
            self,
            graph: Graph,
            colors: list[str],
            seed: int,
            resolution: float,
            labels: dict[int, str]
    ) -> list[Community]:
        communities = louvain_communities(graph, resolution=resolution, seed=seed)
        communities = sorted(communities, key=set.__len__, reverse=True)
        print(f"Detected {len(communities)} communities")

        palette = itertools.cycle(colors)
        result = []
        for community_idx, members in enumerate(communities):
            if len(members) <= Community.SMALL_MAX_SIZE:
                color = Community.SMALL_COLOR
            else:
                color = next(palette)

            community = Community(community_idx, frozenset(members), color, labels.get(community_idx, ''))
            result.append(community)

            if not community.is_small:
                print(f"{community.name} strength: {community.size} with color: {color}")

        small_amount = sum(1 for community in result if community.is_small)
        print(f"{small_amount} communities with <= {Community.SMALL_MAX_SIZE} people with color: {Community.SMALL_COLOR}")

        return result

    def _create_graph(self, df_mutuals: pd.DataFrame):
        graph = nx.Graph()

        for idx, person in df_mutuals.iloc[:].iterrows():
            if len(person['mutuals']) == 0:
                graph.add_node(person['follower_id'])
            else:
                for mutual in person['mutuals']:
                    graph.add_edge(person['follower_id'], mutual['id'])
                    graph.nodes[mutual['id']].setdefault('username', mutual['username'])
            graph.nodes[person['follower_id']]['username'] = person['username']
            # like in the original: the amount of mutuals instagram lists for this person (only your followers count)
            graph.nodes[person['follower_id']]['mutuals'] = len(person['mutuals'])

        print("Nodes: ", graph.number_of_nodes())
        print("Edges: ", graph.number_of_edges())
        return graph

    def _read_followers(self, followers_file: Path, exclude_follower_names):
        with jsonlines.open(followers_file, mode='r') as fd:
            data = [follower for followers_list in fd for follower in followers_list]

        df_followers = pd.DataFrame(data)[['id', 'username']].drop_duplicates()
        df_followers = df_followers[~df_followers['username'].isin(exclude_follower_names)]
        df_followers = df_followers.reset_index(drop=True)

        return df_followers

    def _read_mutuals(self, mutuals_file: Path, df_followers):
        with jsonlines.open(mutuals_file, mode='r') as fd:
            followers_with_mutuals = [follower_with_mutuals for follower_with_mutuals in fd]

        def map_mutuals(x):
            if isinstance(x, dict):
                if x['username'] in df_followers['username'].values:
                    return {'username': x['username'], 'id': x['id']}
                else:
                    return []
            else:
                return []

        df_mutuals = pd.DataFrame(followers_with_mutuals)
        df_mutuals = df_mutuals[df_mutuals['username'] != 'nichtkangs.room']
        df_mutuals = df_mutuals[df_mutuals['username'].isin(df_followers['username'])]
        df_mutuals = df_mutuals.explode('mutuals')
        df_mutuals['mutuals'] = df_mutuals['mutuals'].map(map_mutuals)
        df_mutuals = df_mutuals.groupby(["follower_id", "username"], as_index=False).agg(
            {"mutuals": lambda x: [m for m in x if m]})

        return df_mutuals
