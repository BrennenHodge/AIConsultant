#!/usr/bin/env bash
# FFmpeg mastering for the music bed: room reverb, gentle EQ, fades, -16 LUFS.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/make_music.py assets/music_raw.wav
ffmpeg -y -loglevel error -i assets/music_raw.wav -af "\
aecho=0.8:0.55:60|130|210:0.30|0.22|0.15,\
highpass=f=45,lowpass=f=9500,\
equalizer=f=250:t=q:w=1.2:g=-2,\
afade=t=in:st=0:d=0.6,afade=t=out:st=28.2:d=1.8,\
loudnorm=I=-16:TP=-1.5:LRA=9,\
aresample=48000,apad=whole_dur=30,atrim=0:30" -ar 48000 assets/music.wav
rm assets/music_raw.wav
echo "wrote assets/music.wav"
