from iglink.plot_creator import PlotCreator

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def test_create_plots_writes_images(graph_loader, graph_files, colors, tmp_path):
    plots_dir = tmp_path / 'plots'

    PlotCreator(graph_loader).create_plots(*graph_files, plots_dir, colors, 42, 1.0, [], {0: 'School'})

    for file_name in ['mutuals_distribution.png', 'mutuals_top.png', 'communities.png']:
        assert (plots_dir / file_name).read_bytes().startswith(PNG_SIGNATURE)


def test_create_plots_without_any_connection(graph_loader, graph_files, colors, tmp_path):
    followers_file, mutuals_file = graph_files
    plots_dir = tmp_path / 'plots'
    everybody = ['anna', 'ben', 'cleo', 'dora', 'emil', 'finn', 'gina', 'hugo']

    PlotCreator(graph_loader).create_plots(followers_file, mutuals_file, plots_dir, colors, 42, 1.0, everybody, {})

    assert (plots_dir / 'mutuals_top.png').read_bytes().startswith(PNG_SIGNATURE)
