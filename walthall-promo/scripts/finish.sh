#!/usr/bin/env bash
# FFmpeg finishing: web-optimized H.264/AAC master, poster frame, and QA contact sheet.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -loglevel error -i out/walthall-promo-raw.mp4 \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -tune animation \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
  -metadata title="The Walthall Community Room — Hattiesburg, MS" \
  out/walthall-promo.mp4
ffmpeg -y -loglevel error -ss 7.5 -i out/walthall-promo.mp4 -frames:v 1 -q:v 2 out/poster.jpg
ffmpeg -y -loglevel error -i out/walthall-promo.mp4 \
  -vf "fps=1/2,scale=384:216,tile=5x3:padding=6:color=0x0b1712" -frames:v 1 out/contact-sheet.jpg
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate -of compact out/walthall-promo.mp4
