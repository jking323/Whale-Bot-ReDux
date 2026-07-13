"""Command-line interface for Whale Bot.

    python whale_bot.py ingest local ~/recordings/     # import audio
    python whale_bot.py ingest urls URL [URL ...]      # download audio
    python whale_bot.py ingest manifest urls.txt       # bulk download
    python whale_bot.py process --val-fraction 0.2     # audio+tags -> spectrograms
    python whale_bot.py train   --epochs 15
    python whale_bot.py predict recording.wav
"""

import argparse

from .config import DEFAULT_CHECKPOINT

# Mirrored from model.ARCHITECTURES so the CLI can build its parser without
# importing torch (ingest/process don't need it).
ARCHITECTURES = ("resnet18", "simple")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="whale_bot",
        description="Turn tagged hydrophone recordings into spectrograms and "
                    "train a whale-call classifier.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest: get audio into data/audio/
    p_ingest = sub.add_parser("ingest", help="import or download recordings")
    ingest_sub = p_ingest.add_subparsers(dest="source", required=True)
    p_local = ingest_sub.add_parser("local", help="copy local audio files/dirs")
    p_local.add_argument("path")
    p_local.add_argument("--move", action="store_true",
                         help="move instead of copy")
    p_urls = ingest_sub.add_parser("urls", help="download direct audio URLs")
    p_urls.add_argument("urls", nargs="+")
    p_manifest = ingest_sub.add_parser("manifest", help="download URLs from a file")
    p_manifest.add_argument("path")

    # process: audio + annotations -> spectrogram images
    p_process = sub.add_parser(
        "process", help="build spectrogram dataset from audio + annotations")
    p_process.add_argument("--val-fraction", type=float, default=0.2,
                          help="fraction of segments held out for validation")

    # train
    p_train = sub.add_parser("train", help="train the classifier on spectrograms")
    p_train.add_argument("--epochs", type=int, default=15)
    p_train.add_argument("--batch-size", type=int, default=16)
    p_train.add_argument("--lr", type=float, default=1e-3)
    p_train.add_argument("--arch", choices=ARCHITECTURES, default="resnet18")
    p_train.add_argument("--no-pretrained", action="store_true",
                        help="train from scratch instead of ImageNet weights")
    p_train.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    p_train.add_argument("--num-workers", type=int, default=2)

    # predict
    p_predict = sub.add_parser("predict", help="classify a recording or folder")
    p_predict.add_argument("target", help="audio file or directory of recordings")
    p_predict.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    p_predict.add_argument("--topk", type=int, default=3)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "ingest":
        from . import ingest

        if args.source == "local":
            ingest.import_local(args.path, move=args.move)
        elif args.source == "urls":
            ingest.download_urls(args.urls)
        elif args.source == "manifest":
            ingest.download_manifest(args.path)

    elif args.command == "process":
        from .spectrogram import process

        process(val_fraction=args.val_fraction)

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
