from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class Config:
    data_dir: Path
    profile_pics_dir: Path
    headers_file_name: str
    followers_file_name: str
    mutuals_file_name: str
    output_file_name: str
    stats_file_name: str
    plots_dir: Path

    request_delay_seconds: int
    request_delay_min_deviation: int
    request_delay_max_deviation: int

    followers_pull_max_amount: int
    mutuals_pull_max_amount: int

    graph_width: int
    graph_height: int
    graph_exclude_followers: list[str]
    graph_colors: list[str]
    graph_community_seed: int
    graph_community_resolution: int
    graph_community_labels: dict[int, str]
    graph_initial_position_seed: int


class ConfigLoader(object):

    def load_config(self, config_file: Path):
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)

        return Config(
            data_dir=Path(data['data']['data-dir']),
            profile_pics_dir=Path(data['data']['profile-pics-dir']),
            headers_file_name=data['data']['headers-file-name'],
            followers_file_name=data['data']['followers-file-name'],
            mutuals_file_name=data['data']['mutuals-file-name'],
            output_file_name=data['data']['output-file-name'],
            stats_file_name=data['data']['stats-file-name'],
            plots_dir=Path(data['data']['plots-dir']),

            request_delay_seconds=data['request']['delay-seconds'],
            request_delay_min_deviation=data['request']['delay-deviation-min-seconds'],
            request_delay_max_deviation=data['request']['delay-deviation-max-seconds'],

            followers_pull_max_amount=data['pull-max-amount']['followers'],
            mutuals_pull_max_amount=data['pull-max-amount']['mutuals'],

            graph_width=data['graph']['width'],
            graph_height=data['graph']['height'],
            graph_exclude_followers=data['graph']['exclude-followers'],
            graph_colors=data['graph']['colors'],

            graph_community_seed=data['graph']['community']['seed'],
            graph_community_resolution=data['graph']['community']['resolution'],
            graph_community_labels={
                int(community_id): str(label)
                for community_id, label in (data['graph']['community']['labels'] or {}).items()
            },

            graph_initial_position_seed=data['graph']['initial-position-seed'],
        )


class DataStore:
    BASE_DIR = Path(__file__).resolve().parents[3]
    CONFIG_FILE = BASE_DIR / 'config.yaml'