.. contents: index

===============
Current project
===============

The project is a proper Python package (``whale_bot/``) implementing an
end-to-end bioacoustic pipeline: tagged hydrophone recordings are turned into
mel-spectrogram images and used to train an image classifier.

- ``ingest`` — bring recordings into ``data/audio/`` (local files, direct URLs,
  or a manifest of URLs)
- ``process`` — slice each tagged span, convert to a log-mel spectrogram, and
  save it under ``datasets/spectrograms/{train,val}/<label>/``
- ``train`` — fine-tune a pretrained ResNet18 on the spectrogram images
- ``predict`` — window a recording into spectrograms, classify each, and
  average the scores into one prediction

Tags are supplied *separately* from audio (CSV, Audacity label tracks, or Raven
selection tables) and dropped into ``data/annotations/``. See the repository
README for full setup and usage instructions.
