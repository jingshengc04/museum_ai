"""Cut a character model sheet into separate reference crops without their text labels.

Labels on a reference image leak into generated video, so every crop must be text-free.

  python -m museum.sheet sheet.png --exhibit hope --grid 2x3 \
      --names front,side,calm,curious,delighted,thoughtful --trim 0.05,0.03,0.2,0.03

--grid is rows x columns, --names fills the grid left to right, top to bottom ("-" skips a cell),
--trim cuts a fraction off each cell's top,right,bottom,left (where the labels are).
For an irregular sheet give exact pixel boxes instead:  --box calm=40,620,420,900
Check the crops in exhibits/<id>/refs/ by eye afterwards.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from . import config


def grid_boxes(size: tuple[int, int], rows: int, cols: int, names: list[str], trim: list[float]) -> dict[str, tuple]:
    width, height = size
    cell_w, cell_h = width / cols, height / rows
    top, right, bottom, left = trim
    boxes = {}
    for index, name in enumerate(names):
        if name == "-":
            continue
        row, col = divmod(index, cols)
        boxes[name] = (
            round(col * cell_w + left * cell_w), round(row * cell_h + top * cell_h),
            round((col + 1) * cell_w - right * cell_w), round((row + 1) * cell_h - bottom * cell_h),
        )
    return boxes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--exhibit", required=True)
    parser.add_argument("--grid", help="rows x columns, e.g. 2x3")
    parser.add_argument("--names", default="", help="comma-separated crop names in grid order")
    parser.add_argument("--trim", default="0,0,0,0", help="fraction cut from each cell: top,right,bottom,left")
    parser.add_argument("--box", action="append", default=[], help="name=left,top,right,bottom in pixels")
    args = parser.parse_args()

    image = Image.open(args.sheet).convert("RGB")
    boxes: dict[str, tuple] = {}
    if args.grid:
        rows, cols = (int(v) for v in args.grid.lower().split("x"))
        boxes.update(grid_boxes(image.size, rows, cols, args.names.split(","), [float(v) for v in args.trim.split(",")]))
    for spec in args.box:
        name, _, numbers = spec.partition("=")
        boxes[name] = tuple(int(v) for v in numbers.split(","))
    if not boxes:
        parser.error("give --grid with --names, or at least one --box")

    out_dir = config.EXHIBITS_DIR / args.exhibit / "refs"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, box in boxes.items():
        target = out_dir / f"{name.strip().lower()}.png"
        image.crop(box).save(target)
        print(f"{target.relative_to(config.ROOT)}  {box}")


if __name__ == "__main__":
    main()
