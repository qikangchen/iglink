from pathlib import Path

import jsonlines
import pytest

from iglink.common.graph_loader import GraphLoader

COLORS = ["#4E79A7", "#F28E2B", "#E15759"]

# Two groups of four where everybody knows each other, connected only through dora and emil.
# ida has no connection at all.
GROUPS = [['anna', 'ben', 'cleo', 'dora'], ['emil', 'finn', 'gina', 'hugo']]
BRIDGE = ('dora', 'emil')
ISOLATED = 'ida'


def _person(username: str) -> dict:
    return {'id': f"id_{username}", 'username': username, 'full_name': username.title()}


@pytest.fixture
def graph_files(tmp_path) -> tuple[Path, Path]:
    usernames = [username for group in GROUPS for username in group] + [ISOLATED]

    followers_file = tmp_path / 'followers.jsonl'
    with jsonlines.open(followers_file, 'w') as writer:
        writer.write([_person(username) for username in usernames[:5]])
        writer.write([_person(username) for username in usernames[5:]])

    mutuals_file = tmp_path / 'mutuals.jsonl'
    with jsonlines.open(mutuals_file, 'w') as writer:
        for username in usernames:
            mutuals = [_person(other) for group in GROUPS if username in group for other in group if other != username]
            if username == BRIDGE[0]:
                mutuals.append(_person(BRIDGE[1]))
            # somebody who does not follow you is not part of the graph
            mutuals.append(_person('stranger'))
            writer.write({'follower_id': f"id_{username}", 'username': username, 'mutuals': mutuals})

    return followers_file, mutuals_file


@pytest.fixture
def graph_loader():
    return GraphLoader()


@pytest.fixture
def colors():
    return COLORS
