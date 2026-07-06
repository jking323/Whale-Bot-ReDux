# Whale Bot ReDux

[![Documentation Status](https://readthedocs.org/projects/whale-bot-redux/badge/?version=alpha)](https://whale-bot-redux.readthedocs.io/en/alpha/?badge=alpha)
![License](https://img.shields.io/github/license/jking323/Whale-Bot-ReDux)

Identify whales from their calls. This tool pulls **hydrophone recordings**
and their **separate tag files**, slices the tagged spans into **mel
spectrograms**, and trains a PyTorch image classifier on them. The end goal is
to run recordings — including from your own deployed buoys — through the model
and get the whale species/call type with a confidence score.

## Pipeline

```
audio + tags  ->  process  ->  spectrogram images  ->  train  ->  predict
   (ingest)      (segment +      (datasets/           (ResNet18)   (audio in,
                  mel-spec)       spectrograms/)                     label out)
```

1. **ingest** — bring recordings into `data/audio/` (local files, direct URLs,
   or a manifest of URLs).
2. **tags** — drop the *separate* annotation files into `data/annotations/`.
   Each tag is a labeled time span; see [Annotations](#annotation-formats).
3. **process** — for every tag, slice the audio span, convert it to a log-mel
   spectrogram, and save it as a PNG under
   `datasets/spectrograms/{train,val}/<label>/`. The train/val split is
   deterministic, so re-running is stable.
4. **train** — fine-tune a pretrained ResNet18 on the spectrogram images. The
   best checkpoint (with its class names) is saved to
   `models/whale_classifier.pt`.
5. **predict** — feed in a recording; it's windowed into spectrograms,
   classified, and the per-window scores are averaged into one prediction.

Treating spectrograms as images means a standard CNN with ImageNet transfer
learning works well even with a modest number of labeled calls.

## Setup

Requires Python 3.9+ and the system audio library `libsndfile` (bundled with
`soundfile` wheels on most platforms; on Debian/Ubuntu:
`sudo apt-get install libsndfile1 ffmpeg`).

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# CPU-only machines can slim the torch install:
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Usage

```bash
# 1. get audio into data/audio/
python whale_bot.py ingest local ~/buoy-recordings/      # your own files
python whale_bot.py ingest urls https://.../clip1.wav    # direct links
python whale_bot.py ingest manifest orcasound_urls.txt   # bulk download

# 2. put tag files in data/annotations/  (see below)

# 3. build the spectrogram dataset
python whale_bot.py process --val-fraction 0.2

# 4. train
python whale_bot.py train --epochs 15

# 5. classify new audio
python whale_bot.py predict data/audio/new_recording.wav
```

Run any command with `--help` for options.

## Annotation formats

Tags live in `data/annotations/`, separate from the audio. Three formats are
auto-detected:

**CSV (recommended)** — one row per labeled span:

```csv
audio_file,start,end,label
rec_2024-01-05.wav,12.4,15.1,orca
rec_2024-01-05.wav,88.0,91.2,humpback
rec_2024-01-05.wav,140.0,143.0,noise
```

**Audacity label track** (`rec_2024-01-05.txt` — matched to the `.wav` of the
same name), tab-separated, no header: `start<TAB>end<TAB>label`.

**Raven selection table** (`.txt` with `Begin Time (s)` / `End Time (s)`
columns) — the species/annotation column is picked up automatically.

Include a `noise` (or `background`) label for spans with no whale, so the model
learns to reject empty audio.

## Data sources

- **Orcasound** — open hydrophone archives from the Salish Sea
  (<https://www.orcasound.net>); clips are downloadable via direct URLs.
- **Watkins Marine Mammal Sound Database** — labeled marine mammal calls
  (<https://cis.whoi.edu/science/B/whalesounds/>).
- **NOAA / Kaggle** passive-acoustic datasets — many ship with annotations.
- **Your own buoys** — drop recordings in with `ingest local` and provide tags
  as a CSV.

Spectrogram parameters (sample rate, clip length, FFT size, mel bins) live in
`whale_bot/config.py` and are shared by processing and prediction — change them
in one place.

## Docker

```bash
docker build -t whale-bot .
docker run -v $(pwd)/data:/app/data \
  -v $(pwd)/datasets:/app/datasets \
  -v $(pwd)/models:/app/models \
  whale-bot process
```

Swap the trailing argument for any subcommand (`ingest ...`, `train`,
`predict ...`).

## Project layout

```
whale_bot/
  config.py       paths + audio/spectrogram parameters
  ingest.py       recordings -> data/audio/ (local / URL / manifest)
  annotations.py  parse separate tag files (CSV / Audacity / Raven)
  spectrogram.py  audio + tags -> mel-spectrogram PNGs
  dataset.py      ImageFolder loaders + augmentation
  model.py        ResNet18 transfer learning / SimpleCNN baseline
  train.py        training loop, saves best-val checkpoint
  predict.py      audio -> windowed spectrograms -> averaged prediction
  cli.py          argparse subcommands
whale_bot.py      entry point
```

## Roadmap

- [ ] Live Orcasound feed ingest (pull recent clips on a schedule)
- [ ] Per-window timeline output (when in the recording each call occurs)
- [ ] Buoy field workflow: auto-ingest + nightly retrain
- [ ] Experiment tracking (per-run metrics history)
