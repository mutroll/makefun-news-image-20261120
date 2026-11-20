# makefun-news-image-20261120

A newspaper-style poster that sums up Friday 20 November 2026's world news in one image.

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/mutroll/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/mutroll/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

## What it is

`main.py` (Python 3.13 standard library only, no network) draws a 1024x1024
front page titled "FRIDAY 20 NOVEMBER 2026 — THE WORLD IN ONE DAY" and writes
it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).
It draws everything programmatically — a hand-written 5x7 block font, vector
scenes, and a hand-rolled PNG encoder — so two runs produce byte-identical
output.

## The six stories (all events that happened or were first reported on 20 Nov 2026)

1. **Cyclone Akvan** bears down on Odisha, India — landfall due near
   Gopalpur around noon; 300,000 evacuated, 423 rescue teams deployed.
2. **Asian tech sell-off** — SoftBank -16%, Nikkei -3.7%, Kospi below 5,000.
3. **Japan inflation** — core CPI +2.2% in October, the highest of 2026;
   a December rate rise is now expected.
4. **Taiwan curbs short selling** — new limits take effect today after the
   Taiex lost 5,248 points in three days.
5. **EU to summon Russia's envoy** — after Thursday's Kyiv strikes damaged
   the Austrian and Dutch embassies.
6. **World Children's Day** — the UN marks the rights of the child.

Footer ("Also today"): Fiona the hippo dies at Cincinnati Zoo; day 2 of the
India v New Zealand Test in Wellington; Trump to brief reporters on his
China trip.

Research notes and sources: `../notes-news-20261120.md` (in the workspace,
not part of this repository).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
