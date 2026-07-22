# Holding Breath in Beethoven

This repository packages the reproducibility materials for **"Holding Breath in Beethoven: Active-Silence Strategies in the Grave of the Pathetique,"** submitted to **ISMIR LBD 2026** as a **non-archival** late-breaking demo paper. It contains code, extracted timing features, derived figures, and a documented source manifest for the July 21, 2026 verified study set.

The shipped CSV feature tables are the canonical July 21, 2026 verified outputs used for the draft. Re-running the detector on newly re-obtained audio or a different `ffmpeg` build can shift a small number of pause boundaries.

## What Is Not Here

No audio files are included. The ATEPP-linked WAVs used for the study are copyrighted commercial recordings, so this package ships only code, extracted features, figures, and provenance metadata. To re-obtain the audio, use `data/manifest.csv` and the documented ATEPP/YouTube source links, then place your local files in a separate audio directory.

## Reproduce In Three Commands

Prerequisite: install `ffmpeg` and place your local audio in one directory. The scripts try filenames such as `AB.wav`, `DB.wav`, or the pianist name, for extensions `wav`, `mp3`, `flac`, `m4a`, and `aiff`.

```bash
python3 -m pip install -r requirements.txt
export HB_AUDIO_DIR="/absolute/path/to/local/audio"
python3 code/01_detect.py --audio-dir "$HB_AUDIO_DIR" && python3 code/02_normalize_rerun.py --audio-dir "$HB_AUDIO_DIR" && python3 code/03_analysis.py && python3 code/04_figures.py
```

## Data Dictionary: `data/events.csv`

- `recording_id`: short identifier used throughout the package.
- `pianist`: performer name.
- `pause`: score-localized pause label (`P1`-`P4`).
- `d_s`: sounding duration before the detected low-energy region, in seconds.
- `d_l`: low-energy duration after decay and before the next attack, in seconds.
- `T`: total local pause interval, defined as `d_s + d_l`.
- `condition`: `source` for the source-conditioned baseline run, `peaknorm` for the `-1 dBFS` peak/gain control rerun.
- `threshold_setting`: silence-detector setting used for that row. The shipped event table uses the verified baseline `-35dB_0.10s`.

## Known Limitations

- The boundary detector uses an absolute `dBFS` threshold, so event boundaries remain sensitive to source level and mastering differences.
- The peak-normalized rerun is a simple gain control to `-1 dBFS`, not integrated-loudness normalization; LUFS-based normalization is left to future work.
- `d_s` is not treated as a pure performance variable because it mixes acoustics, transfer, score texture, pedaling, and release behavior.
- The historical Schnabel source is documented in the manifest but excluded from the core event table because ATEPP flags the representative source as background noise.

## How To Cite

Harold Wang, *Holding Breath in Beethoven: Active-Silence Strategies in the Grave of the Pathetique*, submitted to ISMIR LBD 2026.

Contact: haroldw101313@wpga.ca
