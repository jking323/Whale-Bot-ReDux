FROM python:3.11-slim

# libsndfile is required by soundfile/librosa for audio decoding
RUN apt-get update \
    && apt-get install -y --no-install-recommends libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY whale_bot/ whale_bot/
COPY whale_bot.py .

# Mount data/, datasets/, and models/ as volumes so recordings, spectrograms,
# and checkpoints survive container restarts:
#   docker run -v $(pwd)/data:/app/data \
#     -v $(pwd)/datasets:/app/datasets -v $(pwd)/models:/app/models \
#     whale-bot process
ENTRYPOINT ["python", "whale_bot.py"]
CMD ["--help"]
