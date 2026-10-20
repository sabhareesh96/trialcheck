# Version 2: beat-synced shuffle cut, DUBAI title, drone ending

`dubai_beat_sync_final.mp4`: 1080×1920, 30 fps, 15.0 s, AAC audio.
Music: `dubai_bass_track_100bpm.wav`, an original 100 BPM track written for this edit. It's
royalty-free and uses D hijaz (Arabic-scale) plucks, 808 bass, kicks, claps and risers.

## Timeline (100 BPM: 1 beat = 0.6 s = 18 frames)

| Time | Beat | Section | What happens on the bass |
|------|------|---------|--------------------------|
| 0.0–1.2 s | 0–2 | Intro: Ferrari World, starting on her back | Arabic plucks, a reverse cymbal and a riser build into the drop |
| 1.2–4.8 s | 2–8 | Steps: Hollywood → SeaWorld → Dubai Frame → Safari → 101 → Yellow | **Kick + 808 on every cut** (one location per step) |
| 4.8–7.2 s | 8–12 | Shuffle: Safari → Yellow → Hollywood → 101 → SeaWorld → Dubai Frame → Safari shop → Dubai Frame | **808 stab + kick on every eighth note = every cut** (half-step cuts, 0.3 s), with a snare roll and riser |
| 7.2–10.2 s | 12–17 | Desert finale | Sub-boom impact as **DUBAI rises from behind the dune**, letter by letter. She walks in front of it and turns to camera. Half-time groove. |
| 10.2 s | 17 | Whip-pan up | Whoosh into impact |
| 10.2–15.0 s | 17–25 | Drone climb over **DUBAI carved in the sand**, her long sunset shadow beside it | Long 808 and pad, final hijaz phrase, fade to black |

Measured on the rendered track, every cut lands on a bass onset (0–25 ms). Loudness is −10 LUFS
with a −0.6 dBFS peak, which suits Reels and TikTok.

## How each effect was made

- **Shuffle cuts:** a search over half-step gait phases across 9 takes (including alternates 162602,
  162421 and 103953). It keeps her foot rhythm unbroken and holds her size within 3% at every cut,
  so she reads as one continuous walk while the outfits shuffle.
- **Text behind the subject:** her cut-out mask comes from a person-segmentation model (rembg
  u2net_human_seg), clipped to her tracked body box. The dune ridge is traced on a reference frame
  and pinned to the camera's motion by phase correlation. The letters rise from below the ridge
  (hidden by the sand), sit behind her, and pick up a sun glow.
- **Drone shot:** no real drone footage exists and Higgsfield had 0 credits, so it's rendered. It
  combines a dune height map with wind ripples, DUBAI carved in with sand banked around the edges,
  and low-sun lighting with ray-traced cast shadows. Her real silhouette from the desert clip forms
  the long shadow, with a footprint trail leading to her. The drone move is a 2.25×→1× climb with a
  14° turn.
  - A Canva AI version also exists ("Open generated image": https://www.canva.com/M/MAHYl5m1XWo).
    This environment's network can't download from Canva, so it wasn't used.
  - To swap in real or AI drone footage, replace section E in `scripts/v2/render3.py`.

## Swapping the music

To use a licensed song, pick one at 100 BPM, or 200 BPM counted in half-time. Put its first downbeat
at 0.00 s and a big drop at 7.2 s. The cuts in `beat_cues.json` then land on the beat.
