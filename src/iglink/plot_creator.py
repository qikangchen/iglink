import logging
from pathlib import Path

import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from networkx import Graph

from iglink.common.graph_loader import Community, GraphLoader, mutuals_of


class PlotCreator:
    
    DISTRIBUTION_FILE_NAME = 'mutuals_distribution.png'
    TOP_FILE_NAME = 'mutuals_top.png'
    COMMUNITIES_FILE_NAME = 'communities.png'

    TOP_AMOUNT = 20
    DPI = 200

    BAR_COLOR = '#638CF5'
    INK = '#000000'
    TICK_INK = '#333333'
    TITLE_FONTS = ['Arial Black', 'Helvetica Neue', 'Helvetica', 'Arial', 'Liberation Sans', 'DejaVu Sans']

    STYLE = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans'],
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#ffffff',
        'savefig.facecolor': '#ffffff',
        'axes.edgecolor': INK,
        'axes.linewidth': 0.9,
        'axes.labelcolor': TICK_INK,
        'axes.labelsize': 11,
        'xtick.color': INK,
        'ytick.color': INK,
        'xtick.labelcolor': TICK_INK,
        'ytick.labelcolor': TICK_INK,
        'xtick.labelsize': 10.5,
        'ytick.labelsize': 10.5,
    }

    def __init__(self, graph_loader: GraphLoader):
        self.graph_loader = graph_loader

    def create_plots(
            self,
            followers_file: Path,
            mutuals_file: Path,
            plots_dir: Path,
            colors: list[str],
            community_seed: int,
            community_resolution: float,
            exclude_follower_names,
            community_labels: dict[int, str],
    ):
        graph = self.graph_loader.load_graph(followers_file, mutuals_file, exclude_follower_names)
        communities = self.graph_loader.detect_communities(
            graph, colors, community_seed, community_resolution, community_labels)

        plots_dir.mkdir(parents=True, exist_ok=True)
        logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
        with matplotlib.rc_context(self.STYLE):
            self.plot_distribution(graph, plots_dir / self.DISTRIBUTION_FILE_NAME)
            self.plot_top(graph, plots_dir / self.TOP_FILE_NAME)
            self.plot_communities(communities, plots_dir / self.COMMUNITIES_FILE_NAME)

    def plot_distribution(self, graph: Graph, output_file: Path):
        """How many people have how many mutuals. Every amount of mutuals gets its own bar."""
        amounts = [mutuals_of(graph, node) for node in graph.nodes()] or [0]

        fig = Figure(figsize=(7.8, 6.6), dpi=self.DPI, layout='constrained')
        ax = fig.add_subplot()
        ax.hist(amounts, bins=range(0, max(amounts) + 2), color=self.BAR_COLOR, linewidth=0)

        ax.set_xlabel("Mutuals")
        ax.set_ylabel("Amount of people")
        ax.set_xticks(range(0, max(amounts) + 1, 5))
        ax.yaxis.set_major_locator(self._locator())
        ax.set_xlim(-max(amounts) * 0.05 - 1, max(amounts) * 1.05 + 1)
        self._add_title(ax, "Mutual distribution")

        self._save(fig, output_file)

    def plot_top(self, graph: Graph, output_file: Path):
        """The people with the most mutuals."""
        mutuals = {node: mutuals_of(graph, node) for node in graph.nodes()}
        ranked = sorted(mutuals, key=lambda node: (-mutuals[node], graph.nodes[node].get('username', '')))
        ranked = [node for node in ranked[:self.TOP_AMOUNT] if mutuals[node] > 0]

        self._plot_ranking(
            "Top mutuals",
            [graph.nodes[node].get('username', 'unknown') for node in ranked],
            [mutuals[node] for node in ranked],
            [self.BAR_COLOR] * len(ranked),
            "Mutuals",
            output_file
        )

    def plot_communities(self, communities: list[Community], output_file: Path):
        """The size of each community, in the colors of the graph."""
        big_communities = [community for community in communities if not community.is_small]
        without_community = sum(community.size for community in communities if community.is_small)

        names = [community.name for community in big_communities]
        sizes = [community.size for community in big_communities]
        colors = [community.color for community in big_communities]
        if without_community > 0:
            names.append("No community")
            sizes.append(without_community)
            colors.append(Community.SMALL_COLOR)

        self._plot_ranking("Community sizes", names, sizes, colors, "Amount of people", output_file)

    def _plot_ranking(
            self,
            title: str,
            names: list[str],
            values: list[int],
            colors: list[str],
            value_label: str,
            output_file: Path
    ):
        row_amount = max(len(names), 1)

        fig = Figure(figsize=(7.8, 0.32 * row_amount + 2.2), dpi=self.DPI, layout='constrained')
        ax = fig.add_subplot()
        ax.barh(range(len(values)), values, height=0.8, color=colors, linewidth=0)

        ax.set_yticks(range(len(names)), names)
        ax.set_ylim(row_amount - 0.4, -0.6)
        ax.set_xlim(0, max(values, default=1) * 1.05)
        ax.xaxis.set_major_locator(self._locator())
        ax.set_xlabel(value_label)
        self._add_title(ax, title)

        self._save(fig, output_file)

    def _locator(self) -> MaxNLocator:
        return MaxNLocator(nbins=7, integer=True, steps=[1, 2, 5, 10])

    def _add_title(self, ax: Axes, title: str):
        ax.set_title(
            title.upper(), loc='left', pad=22, fontsize=26, fontweight='black', color=self.INK,
            fontfamily=self.TITLE_FONTS
        )

    def _save(self, fig: Figure, output_file: Path):
        fig.get_layout_engine().set(w_pad=0.25, h_pad=0.25)
        fig.savefig(output_file)
        print(f"Saved plot to {output_file}")
