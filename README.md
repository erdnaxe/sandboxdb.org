# Grimorio

Grimorio collects daemons from various GNU/Linux distributions.

## Repository structure

  * `assets/`, `layouts/` and `static/` are frontend files for the static
    website,
  * `data/` is the folder containing the database in JSON format,
  * `scripts/` contains Python scripts to generate the database in `data/`.

## How to build locally

You need to have [Hugo](https://gohugo.io/) and Python installed.

You can then launch scripts in `scripts/` to scrap data from upstream
distributions.

Then you can launch a local instance using `hugo server` or build the static
website using `hugo`.
