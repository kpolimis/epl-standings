.DEFAULT_GOAL := help

.PHONY: help all data html trajectories cluster elbow test clean refresh

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

all: html trajectories  ## Build index.html and trajectories.html

data: data/standings_verified.json  ## Fetch verified standings (cached)

data/standings_verified.json:
	python fetch_standings.py

refresh:  ## Re-fetch all sources, ignoring cache
	python fetch_standings.py --refresh

html: index.html  ## Generate the bump chart (index.html)

index.html: generate.py html_template.py team_config.py data/standings_verified.json
	python generate.py

trajectories: trajectories.html  ## Generate the cluster sparkline chart

trajectories.html: generate_trajectories.py trajectories_template.py clustering.py data/standings.json
	python generate_trajectories.py

cluster:  ## Print cluster summary to stdout
	python cluster_trajectories.py

elbow:  ## Regenerate docs/elbow.png (k-selection chart)
	python elbow_analysis.py

test:  ## Run pytest suite
	pytest tests/ -v

clean:  ## Remove generated HTML outputs (keeps cache + data)
	rm -f index.html trajectories.html
