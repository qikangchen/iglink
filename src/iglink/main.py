import argparse

from iglink.common.config import ConfigLoader, DataStore
from iglink.common.follower_reader import FollowersReader
from iglink.common.graph_loader import GraphLoader
from iglink.common.header_extractor import HeaderExtractor
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader import follower_downloader
from iglink.downloader.pagination_downloader import PaginationDownloader
from iglink.downloader.follower_downloader import FollowerDownloader
from iglink.downloader.mutual_downloader import MutualDownloader
from iglink.downloader.profile_pic_downloader import ProfilePicDownloader
from iglink.graph_creator import GraphCreator
from iglink.plot_creator import PlotCreator
from iglink.stats_creator import StatsCreator


class Main:

    def __init__(self):
        self.data_store = DataStore()
        self.config = ConfigLoader().load_config(self.data_store.CONFIG_FILE)

        header_extractor = HeaderExtractor(self.config.data_dir / self.config.headers_file_name)
        http_client = HttpClient(header_extractor.get_headers())

        request_delayer = RequestDelayer(
            self.config.request_delay_seconds,
            self.config.request_delay_min_deviation,
            self.config.request_delay_max_deviation
        )

        follower_reader = FollowersReader()
        pagination_downloader = PaginationDownloader(request_delayer)

        self.follower_downloader = FollowerDownloader(
            http_client,
            request_delayer,
            header_extractor.get_ig_id(),
            self.config.followers_pull_max_amount,
            pagination_downloader
        )

        self.profile_pic_downloader = ProfilePicDownloader(
            http_client,
            request_delayer,
            follower_reader
        )

        self.mutual_downloader = MutualDownloader(
            http_client,
            request_delayer,
            follower_reader,
            self.config.mutuals_pull_max_amount,
            pagination_downloader
        )

        graph_loader = GraphLoader()
        self.graph_creator = GraphCreator()
        self.stats_creator = StatsCreator(graph_loader)
        self.plot_creator = PlotCreator(graph_loader)

    def download_followers(self):
        self.follower_downloader.download_followers(self.config.data_dir / self.config.followers_file_name)

    def download_profile_pics(self):
        self.profile_pic_downloader.download_profile_pics(
            self.config.data_dir / self.config.followers_file_name,
            self.config.data_dir / self.config.profile_pics_dir
        )

    def download_mutuals(self):
        self.mutual_downloader.download_mutuals(
            self.config.data_dir / self.config.followers_file_name,
            self.config.data_dir / self.config.mutuals_file_name
        )

    def create_graph(self):
        self.graph_creator.create_graph(
            self.config.data_dir / self.config.followers_file_name,
            self.config.data_dir / self.config.mutuals_file_name,
            self.config.data_dir / self.config.profile_pics_dir,
            self.config.data_dir / self.config.output_file_name,
            self.config.graph_colors,
            self.config.graph_width,
            self.config.graph_height,
            self.config.graph_community_seed,
            self.config.graph_community_resolution,
            self.config.graph_initial_position_seed,
            self.config.graph_exclude_followers,
        )

    def create_stats(self):
        self.stats_creator.create_stats(
            self.config.data_dir / self.config.followers_file_name,
            self.config.data_dir / self.config.mutuals_file_name,
            self.config.data_dir / self.config.stats_file_name,
            self.config.graph_colors,
            self.config.graph_community_seed,
            self.config.graph_community_resolution,
            self.config.graph_exclude_followers,
            self.config.graph_community_labels,
        )

    def create_plots(self):
        self.plot_creator.create_plots(
            self.config.data_dir / self.config.followers_file_name,
            self.config.data_dir / self.config.mutuals_file_name,
            self.config.data_dir / self.config.plots_dir,
            self.config.graph_colors,
            self.config.graph_community_seed,
            self.config.graph_community_resolution,
            self.config.graph_exclude_followers,
            self.config.graph_community_labels,
        )


if __name__ == '__main__':
    program = Main()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest='command',
        required=True
    )

    download_followers = subparsers.add_parser('download_followers')
    download_profile_pics = subparsers.add_parser('download_profile_pics')
    download_mutuals = subparsers.add_parser('download_mutuals')
    create_graph = subparsers.add_parser('create_graph')
    create_stats = subparsers.add_parser('create_stats')
    create_plots = subparsers.add_parser('create_plots')

    args = parser.parse_args()
    if args.command == 'download_followers':
        program.download_followers()
    elif args.command == 'download_profile_pics':
        program.download_profile_pics()
    elif args.command == 'download_mutuals':
        program.download_mutuals()
    elif args.command == 'create_graph':
        program.create_graph()
    elif args.command == 'create_stats':
        program.create_stats()
    elif args.command == 'create_plots':
        program.create_plots()
