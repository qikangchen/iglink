from iglink.common.graph_loader import Community, mutuals_of


def test_load_graph_connects_followers_with_their_mutuals(graph_loader, graph_files):
    graph = graph_loader.load_graph(*graph_files, [])

    assert graph.number_of_nodes() == 9
    assert graph.number_of_edges() == 13
    assert graph.has_edge('id_dora', 'id_emil')
    assert graph.degree['id_ida'] == 0
    assert graph.nodes['id_anna']['username'] == 'anna'


def test_load_graph_counts_the_mutuals_of_each_person(graph_loader, graph_files):
    graph = graph_loader.load_graph(*graph_files, [])

    # emil is in the mutuals of dora, but dora is not in the mutuals of emil. stranger does not follow you
    assert mutuals_of(graph, 'id_dora') == 4
    assert mutuals_of(graph, 'id_emil') == 3
    assert graph.degree['id_emil'] == 4
    assert mutuals_of(graph, 'id_ida') == 0


def test_load_graph_ignores_people_who_are_not_followers(graph_loader, graph_files):
    graph = graph_loader.load_graph(*graph_files, [])

    assert 'id_stranger' not in graph


def test_load_graph_excludes_followers(graph_loader, graph_files):
    graph = graph_loader.load_graph(*graph_files, ['anna'])

    assert 'id_anna' not in graph
    assert graph.number_of_nodes() == 8
    assert graph.degree['id_ben'] == 2


def test_detect_communities_sorts_colors_and_labels_them(graph_loader, graph_files, colors):
    graph = graph_loader.load_graph(*graph_files, [])

    communities = graph_loader.detect_communities(graph, colors, 42, 1.0, {0: 'School'})

    assert [community.size for community in communities] == [4, 4, 1]
    assert [community.color for community in communities] == [colors[0], colors[1], Community.SMALL_COLOR]
    assert [community.name for community in communities] == ['School', 'Community #1', 'Community #2']
    assert [community.is_small for community in communities] == [False, False, True]
    assert communities[2].members == {'id_ida'}
