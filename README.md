# IGLINK
IG LInked NetworK (IGLINK) is a tool to create an interactive map with all your instagram followers and mutuals.

It uses the Louvain Community Detection algorithm to categorize your followers into communities.

![Overview](static/overview.png)  
![Overview zoomed in](static/overview-zoomed.png)  

# Warning
Use at your own risk. Because a lot of data is pulled form instagram, they can sometimes think you are a bot and can ban you.
This is why in `config.yaml` the `request->delay-seconds` are set pretty high to prevent bot detection.

# Installment
- After installing uv use: `uv sync`
- To activate the python env: `source .venv/bin/activate`

# Settings
- Fill `headers.txt`. This is your login data from instagram
  - Use firefox
  - Navigate to you IG profile and open your developer console and open the network tab
  - Click on followers
  - Search in the network tab for `https://www.instagram.com/api/v1/friendships/<id>/followers/?count=12&search_surface=follow_list_page`
  - Right Click -> Copy Value -> Copy Request Headers
  - Replace all content with the copied values in `data/headers.txt`
- look into `config.yaml` for your settings. Default values are provided and should be fine to use. Read comments in the file, if you want to change.

# Usage
Steps:
- all data will be stored in `data/`
- `python -m src.iglink.main download_followers`
  - if an error occurs, delete 'data/followers.jsonl' and run again
- `python -m src.iglink.main download_profile_pics`
  - if an error occurs, run again, it will pick up from the last checkpoint
- `python -m src.iglink.main download_mutuals`
  - if an error occurs, run again, it will pick up from the last checkpoint
- `python -m src.iglink.main create_graph`
- `python -m src.iglink.main create_stats` (optional)
  - prints statistics about your followers and their communities and stores them in `data/stats.json`
- `python -m src.iglink.main create_plots` (optional)
  - stores three plots in `data/plots/`: how many mutuals people have, who has the most mutuals and how big the communities are
  - you can name the communities in `config.yaml` under `graph -> community -> labels`, i.e. `{0: 'School', 1: 'Work'}`. The names are used in the statistics and plots

Now you can open the resulting .html file in the data folder.

# TODO
- [ ] Rewrite test: use stubs