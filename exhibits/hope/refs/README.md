# Character reference crops

Drop Hope's reference images here, one per file, **with no text labels** (labels leak into generated video).
The file name is the name a storyboard shot uses in its `refs` list.

The storyboards expect: `front.png`, `side.png`, `calm.png`, `curious.png`, `delighted.png`, `thoughtful.png`.

To cut them from the labelled model sheet:

    python -m museum.sheet path/to/sheet.png --exhibit hope --grid 2x3 \
        --names front,side,calm,curious,delighted,thoughtful --trim 0.05,0.03,0.2,0.03

Adjust `--grid` and `--trim` to the sheet, then check every crop by eye. Any extra image here (for example
`hall.jpg`) is also usable by name. A shot that names no existing crop falls back to the first few in this folder.
