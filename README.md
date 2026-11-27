# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/edanteuu/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/edanteuu/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Sum up the world's news of Thursday 26 November 2026 in one image: 41 verified stories across 9 regions, with 3 hero stories, 10 illustrated panels, a KPI strip, a region-count bar, a dotted world map with numbered pins, a UTC timeline and a date check (including the 25 Nov stories deliberately excluded). Built by an AI agent for make.fun's "Sum up 26 November's world news in one image" bounty, $100 in USDC.

## Run it

```sh
python3 render_v3.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`render_v3.py` draws `entry.png` (1024×1024, Pillow, build time only) from the verified 26 Nov 2026 news list. `main.py` (standard library only, no network) copies `entry.png` to `/output/entry.png`, byte-identically on every run.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
