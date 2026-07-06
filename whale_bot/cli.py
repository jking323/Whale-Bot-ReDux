"""Command-line interface for Whale Bot.

    python whale_bot.py scrape   --subreddit whales --limit 100 --listing top
    python whale_bot.py download
    python whale_bot.py train    --epochs 10
    python whale_bot.py predict  path/to/image.jpg
"""

import argparse

from .config import DEFAULT_CHECKPOINT

# Mirrored from model.ARCHITECTURES / scraper.LISTINGS so the CLI can build
# its parser without importing torch (scrape/download work torch-free)
ARCHITECTURES = ("resnet18", "simple")
LISTINGS = ("hot", "new", "top")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="whale_bot",
        description="Scrape whale photos from Reddit and train a classifier.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scrape = sub.add_parser("scrape", help="log subreddit posts to data/posts.csv")
    p_scrape.add_argument("--subreddit", default="whales")
    p_scrape.add_argument("--limit", type=int, default=50)
    p_scrape.add_argument("--listing", choices=LISTINGS, default="hot")

    sub.add_parser("download", help="download logged images to datasets/raw/")

    p_train = sub.add_parser("train", help="train the classifier")
    p_train.add_argument("--epochs", type=int, default=10)
    p_train.add_argument("--batch-size", type=int, default=16)
    p_train.add_argument("--lr", type=float, default=1e-3)
    p_train.add_argument("--arch", choices=ARCHITECTURES, default="resnet18")
    p_train.add_argument(
        "--no-pretrained",
        action="store_true",
        help="train from scratch instead of ImageNet weights",
    )
    p_train.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    p_train.add_argument("--num-workers", type=int, default=2)

    p_predict = sub.add_parser("predict", help="classify an image or folder")
    p_predict.add_argument("target", help="image file or directory of images")
    p_predict.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    p_predict.add_argument("--topk", type=int, default=3)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    # Import lazily so `scrape`/`download` work without torch installed
    if args.command == "scrape":
        from .scraper import scrape

        scrape(subreddit=args.subreddit, limit=args.limit, listing=args.listing)
    elif args.command == "download":
        from .downloader import download_images

        download_images()
    elif args.command == "train":
        from .train import train

        train(
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            arch=args.arch,
            pretrained=not args.no_pretrained,
            checkpoint=args.checkpoint,
            num_workers=args.num_workers,
        )
    elif args.command == "predict":
        from .predict import predict

        predict(args.target, checkpoint=args.checkpoint, topk=args.topk)


if __name__ == "__main__":
    main()
