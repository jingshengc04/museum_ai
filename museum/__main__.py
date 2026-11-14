"""Command line: python -m museum <serve|make|promote|status|check>"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import config, exhibits, pipeline


def _print_event(kind: str, **data) -> None:
    if kind == "thought":
        print(f"  {'!' if data.get('level') == 'warn' else '·'} {data['text']}")
    elif kind == "step":
        if data["status"] == "start":
            print(f"[{data['step']}]")
    elif kind == "storyboard":
        print(f"  “{data['title']}” ({data['origin']}, {len(data['shots'])} shots)")


def status() -> None:
    print("Modes (set LIVE=llm,voice,video to go live):")
    for name, m in config.modes().items():
        print(f"  {name:6} {m['reason']}")
    print(f"Video: {config.VIDEO_MODEL} at {config.VIDEO_RESOLUTION} {config.VIDEO_ASPECT}, "
          f"${config.clip_price_usd(config.VIDEO_MAX_SECONDS):.2f} per {config.VIDEO_MAX_SECONDS} s clip, budget ${config.MAX_FAL_USD:.2f}/film")
    for exhibit in exhibits.all_exhibits():
        print(f"Exhibit '{exhibit.id}': {exhibit.name}")
        print(f"  facts with a source: {len(exhibit.facts)}, without: {len(exhibit.unsourced_facts)}")
        print(f"  photo: {exhibit.photo.name if exhibit.photo else 'none (drop photo.jpg in the exhibit folder)'}")
        print(f"  refs:  {', '.join(sorted(exhibit.refs)) or 'none (drop crops into refs/)'}")
        print(f"  storyboards: {', '.join(p.stem for p in sorted(exhibit.dir.glob('storyboards/*.json'))) or 'none'}")
        print(f"  overrides:   {', '.join(p.name for p in sorted(exhibit.dir.glob('overrides/*')) if p.name != 'README.md') or 'none'}")
        print(f"  film library: {', '.join(d['language'] + '-' + d['style'] for d in exhibit.demos()) or 'none'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="museum", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="run the web app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    make = sub.add_parser("make", help="make one film from the command line")
    make.add_argument("--exhibit", default=None)
    make.add_argument("--photo", type=Path, default=None)
    make.add_argument("--lang", choices=list(config.LANGUAGES), default="en")
    make.add_argument("--style", choices=list(config.STYLES), default="first_person")
    make.add_argument("--no-save", action="store_true", help="do not add the film to the library")

    promote = sub.add_parser("promote", help="put a finished job in the library, e.g. to bring back an earlier take")
    promote.add_argument("job", help="job id (folder name under output/)")
    promote.add_argument("--force", action="store_true")

    sub.add_parser("status", help="show modes, prices and what material each exhibit has")
    sub.add_parser("check", help="test every API key and endpoint with free calls that spend no credits")
    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "check":
        from . import check

        sys.exit(0 if check.run() else 1)
    elif args.command == "serve":
        import uvicorn

        uvicorn.run("museum.server:app", host=args.host, port=args.port)
    elif args.command == "make":
        job_dir = config.OUTPUT_DIR / time.strftime("%m%d-%H%M%S")
        try:
            manifest, _ = pipeline.make_film(job_dir, args.lang, args.style, _print_event, photo=args.photo,
                                             exhibit_id=args.exhibit, fresh=True, save=not args.no_save)
        except Exception as error:  # the CLI reports any failure the same way
            sys.exit(f"Failed: {error}")
        print(f"\n{job_dir / 'final.mp4'}  ({manifest['duration']:.1f}s, fal ${manifest['fal_cost_usd']:.2f}, "
              f"made in {manifest['seconds_to_make']}s)")
    elif args.command == "promote":
        try:
            print(f"Saved to the library: {pipeline.promote(config.OUTPUT_DIR / args.job, force=args.force)}")
        except (RuntimeError, FileNotFoundError) as error:
            sys.exit(f"Failed: {error}")


if __name__ == "__main__":
    main()
