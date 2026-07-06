.. contents: index

===============
Current project
===============

The project has been restructured into a proper Python package (``whale_bot/``)
with a working end-to-end pipeline:

- ``scrape`` — log subreddit posts to ``data/posts.csv`` (deduplicated on re-runs)
- ``download`` — fetch direct image links into ``datasets/raw/``
- ``train`` — fine-tune a pretrained ResNet18 on hand-labeled class folders
- ``predict`` — classify an image or folder with a saved checkpoint

Reddit credentials now come from environment variables (see ``.env.example``)
instead of being hard-coded. See the repository README for full setup and
usage instructions.
