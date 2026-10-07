import json

import pytest

from iglink.stats_creator import StatsCreator


@pytest.fixture
def stats_creator(graph_loader):
    return StatsCreator(graph_loader)


def test_calculate_stats(stats_creator, graph_loader, graph_files, colors):
    graph = graph_loader.load_graph(*graph_files, [])
    communities = graph_loader.detect_communities(graph, colors, 42, 1.0, {0: 'School'})

    stats = stats_creator.calculate_stats(graph, communities)

    assert stats['people'] == 9
    assert stats['connections'] == 13
    assert stats['isolated_people'] == 1
    assert stats['mutuals_per_person'] == {'mean': 2.78, 'median': 3, 'max': 4}
    assert stats['largest_connected_group'] == 8
    assert stats['cross_community_connections'] == 1
    assert stats['people_without_community'] == 1
    assert [(community['name'], community['people'], community['connections_inside'])
            for community in stats['communities']] == [('School', 4, 6), ('Community #1', 4, 6)]
    assert stats['most_mutuals'][0] == {
        'username': 'dora', 'mutuals': 4, 'connections': 4, 'cross_community_connections': 1, 'community': 'School'
    }
    assert [person['username'] for person in stats['most_cross_community_connections']] == ['dora', 'emil']


def test_create_stats_writes_file(stats_creator, graph_files, colors, tmp_path):
    stats_file = tmp_path / 'stats.json'

    stats_creator.create_stats(*graph_files, stats_file, colors, 42, 1.0, [], {})

    with open(stats_file, encoding='utf-8') as fd:
        assert json.load(fd)['people'] == 9
