# Walthall Community Room — 30s promo

1920×1080 · 30 fps · 30 s · H.264/AAC → `out/walthall-promo.mp4` (poster: `out/poster.jpg`)

| Time | Scene |
|---|---|
| 0–4.5s | "A landmark since 1902": the Walthall School facade (Mission Revival, round-arch windows) draws itself in |
| 4.5–9s | Title card: *The Walthall Community Room*, remodeled 2025, now booking |
| 9–14.25s | The room: four tall windows with sunlight across a meeting table |
| 14.25–20.25s | Built for business: boardroom → classroom → banquet floor plans; meetings, trainings, luncheons/receptions |
| 20.25–25.5s | Amenities: full kitchen + service counter, tables & chairs, Walthall Park access, hourly rates |
| 25.5–30s | Call to action: 601 Court Street · hattiesburghistoric@gmail.com · walthall-community-room.vercel.app |

## Pipeline
- **HyperFrames**: `index.html` is the composition (GSAP timeline, local fonts/GSAP, no network needed)
- **FFmpeg**: `scripts/master_audio.sh` masters the synthesized music bed (`scripts/make_music.py`); `scripts/finish.sh` encodes the web master, poster and contact sheet
- **Playwright**: `scripts/storyboard.mjs` seeks the timeline and screenshots key frames for QA

```bash
npm install
npm run music        # assets/music.wav
npm run check        # hyperframes lint/runtime/layout/contrast
npm run storyboard   # out/storyboard.png
npm run render       # out/walthall-promo-raw.mp4
npm run finish       # out/walthall-promo.mp4, poster.jpg, contact-sheet.jpg
```
To render with the preinstalled Chromium in this sandbox, set `HYPERFRAMES_BROWSER_PATH` to the Chromium binary.
