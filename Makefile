.DEFAULT_GOAL := help

.PHONY: help all data html trajectories cluster clean

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

all: html trajectories  ## Build index.html and trajectories.html

data: data/standings_verified.json  ## Fetch verified standings from source

data/standings_verified.json:
	python fetch_standings.py

html: index.html  ## Generate the bump chart (index.html)

index.html: generate.py
	python generate.py

trajectories: trajectories.html  ## Generate the cluster sparkline chart

trajectories.html: data/standings.json generate_trajectories.py
	python generate_trajectories.py

cluster:  ## Print cluster summary to stdout
	python cluster_trajectories.py

clean:  ## Remove generated outputs (not fetched data)
	rm -f index.html trajectories.html
