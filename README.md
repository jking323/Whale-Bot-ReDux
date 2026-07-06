# Whale Bot ReDux

[![Documentation Status](https://readthedocs.org/projects/whale-bot-redux/badge/?version=alpha)](https://whale-bot-redux.readthedocs.io/en/alpha/?badge=alpha)
![License](https://img.shields.io/github/license/jking323/Whale-Bot-ReDux)

A Reddit bot that collects whale photos and trains a PyTorch image classifier
to identify whale species. End goal: scan posts, decide whether the image is a
whale, and comment with the species and a confidence percentage.

## Pipeline

```
scrape  ->  download  ->  label (manual)  ->  train  ->  predict
```

1. **scrape** — log posts from a subreddit (default r/whales) to `data/posts.csv`.
   Re-running only appends posts it hasn't seen before.
2. **download** — fetch every direct image link from the log into
   `datasets/raw/`, named `<post_id>.jpg` so images trace back to their post.
3. **label** — sort images from `datasets/raw/` into class folders by hand:

   ```
   datasets/train/humpback/*.jpg
   datasets/train/orca/*.jpg
   datasets/train/not_a_whale/*.jpg
   datasets/val/humpback/*.jpg        # hold out ~20% of each class
   datasets/val/orca/*.jpg
   datasets/val/not_a_whale/*.jpg
   ```

   Class names are just the folder names — add a species by adding a folder.
   Include a `not_a_whale` class so the model can reject non-whale posts.
4. **train** — fine-tune a pretrained ResNet18 (good results with only a few
   hundred images). The best checkpoint is saved to `models/whale_classifier.pt`.
5. **predict** — classify a single image or a whole folder.

## Setup

Requires Python 3.9+.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# CPU-only machines can slim the torch install:
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

Create a Reddit "script" app at <https://www.reddit.com/prefs/apps>, then:

```bash
cp .env.example .env   # and fill in REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET
```

> **Never commit `.env` or hard-code credentials** — `.gitignore` already
> excludes it.

## Usage

```bash
python whale_bot.py scrape --subreddit whales --limit 100 --listing top
python whale_bot.py download
# ...sort datasets/raw/ into datasets/train/ and datasets/val/ ...
python whale_bot.py train --epochs 10
python whale_bot.py predict datasets/raw/           # or a single image path
```

Useful training flags: `--batch-size`, `--lr`, `--arch simple` (from-scratch
CNN baseline), `--no-pretrained`. Run any command with `--help` for details.

## Docker

```bash
docker build -t whale-bot .
docker run --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/datasets:/app/datasets \
  -v $(pwd)/models:/app/models \
  whale-bot scrape --limit 100
```

Swap the trailing arguments for any other subcommand (`download`, `train`,
`predict ...`).

## Project layout

```
whale_bot/
  config.py      paths + Reddit credentials (from env / .env)
  scraper.py     subreddit posts -> data/posts.csv
  downloader.py  image links -> datasets/raw/
  dataset.py     ImageFolder loaders + augmentation
  model.py       ResNet18 transfer learning / SimpleCNN baseline
  train.py       training loop, checkpoints best val accuracy
  predict.py     inference on files or folders
  cli.py         argparse subcommands
whale_bot.py     entry point
```

## Roadmap

- [ ] Auto-label bootstrap: use post titles ("humpback", "orca"...) to pre-sort raw images
- [ ] Bot mode: watch new posts, classify, and reply with species + confidence
- [ ] Duplicate-image detection before download
- [ ] Experiment tracking (per-run metrics history)
