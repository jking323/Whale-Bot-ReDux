FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY whale_bot/ whale_bot/
COPY whale_bot.py .

# Mount data/, datasets/, and models/ as volumes so scraped posts, images,
# and checkpoints survive container restarts:
#   docker run --env-file .env -v $(pwd)/data:/app/data \
#     -v $(pwd)/datasets:/app/datasets -v $(pwd)/models:/app/models \
#     whale-bot scrape --limit 100
ENTRYPOINT ["python", "whale_bot.py"]
CMD ["--help"]
