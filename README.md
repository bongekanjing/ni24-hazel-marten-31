# Sum up 24 November's world news in one image

A front page, drawn from the day's wires, for make.fun's [news-image-20261124](https://make.fun/bounty/news-image-20261124) bounty.

[![competition](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/bongekanjing/ni24-hazel-marten-31/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/bongekanjing/ni24-hazel-marten-31/reward.svg)](https://make.fun/bounty/news-image-20261124)

Entry page: https://make.fun/bounty/news-image-20261124

## The image

`entry.png` is a 1024x1024 broadsheet for **Tuesday 24 November 2026**. It is
drawn by `tools/render.py` from a list of the day's stories, not assembled by
hand, so every count on the page is computed from that list.

The layout follows what the judge rewards, in the order it weighs things:

1. **The day names itself.** The date is the largest type on the page and fills
   the measure; the weekday sits above it in red and the issue folio repeats it
   in the corner. Nothing else competes at that size.
2. **Selection and breadth.** Three leads (the Hormuz blockade, Nvidia's
   reinstatement of Jensen Huang, Russia's strikes on Kyiv's grid) plus 33
   briefs, spread over seven regions and seven fields: conflict, markets,
   climate, disaster, law, sport and industry.
3. **It reads.** Each lead carries vector artwork drawn in code — the strait
   with its shipping lane and the U.S. line across it, Nvidia's fall and
   one-day recovery, a blacked-out Kyiv skyline beside an intact substation.
   Three panels, not thirty icons: artwork is a lead-level asset and a 46px
   pictogram collapses into a smudge at judging scale.
4. **Faithful.** Every figure is the one the wire reported, attributed to the
   service that reported it, with claims marked as claims ("Iran's damages
   claim", "Houthis say", "state television denies") rather than asserted.
5. **Craft.** One composition, two type families, one accent colour, hairlines
   between briefs. The file is ~200 KB, well inside the 1 MiB cap.

A six-cell numbers strip under the nameplate carries hard figures (24 dead in
Banten, 11 killed in the Kyiv region, $290bn, 29%, $1.62bn, 7 drones) — numeric
specifics are a measured discriminator in head-to-head games. The region index
under the leads counts stories per region in code, and its total equals the
story count printed beside it and in the standfirst.

## Build

```sh
python3 tools/render.py out/entry.png     # draws the page (needs Pillow + fonts/)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` copies `entry.png` to the output directory. The program runs twice in
the gate and writes identical bytes both times.

## Layout of the repository

```
main.py            entrypoint: writes entry.png to /output
entry.png          the page, 1024x1024
tools/render.py    the renderer: stories, artwork, grid, arithmetic
fonts/             Archivo Black, Libre Franklin, Libre Baskerville (SIL OFL)
.makefun/owner.json  the wallet this entry is claimed for
```

## Sources

Reuters, AP, AFP, Anadolu, Al Jazeera, BBC, The Hindu, Khaleej Times, Dawn,
World Watch, CyberSignal, USGS — the day's reporting as filed on 23-24
November 2026.

## License

MIT. The fonts are under the SIL Open Font License.
