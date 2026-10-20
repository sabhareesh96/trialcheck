# Walk-transition edit: clip audit and cut list

Source: Google Drive folder "Achu" (26 phone clips, 24–28 Nov 2024, all 1080×1920 portrait, ~30 fps).
Output: `walk_transition_final.mp4`, 1080×1920, 30 fps, 7.77 s, silent (add a 100 BPM track, see below).

## The concept, as the footage allows

The pasted prompt describes an AI shot of a subject walking **toward** the camera. The footage is the
reverse: the phone starts on her back and she walks **away**, then turns around. The edit applies the
prompt's rules to that motion:

- **Cut on the downstep.** There is one location per step, and every cut lands on a heel strike.
- **Identical subject scale and position.** Inside each step a subject-locked digital push-in
  (1.06×–1.42×) keeps her at the same height and position. At the cut, the next clip opens with her
  at the same size, so the frame acts like a tracking camera at constant distance.
- **Foot parity is preserved.** If the left foot plants at the end of one shot, the next shot opens
  on the left foot planting. The gait never double-steps.
- **Same walking rhythm.** Every step is retimed to exactly 18 frames (0.6 s = 100 BPM). Speed
  changes are 0.92–1.02×, which is invisible.

## Timeline (all cuts are on a 100 BPM beat)

| # | Out time | Location | Take | Source frames | Foot at cut |
|---|----------|----------|------|---------------|-------------|
| 1 | 0.00–1.20 | Ferrari World (opening from back close-up) | video_20241124_111755 | 2–37 | → L |
| 2 | 1.20–1.80 | Hollywood street (indoor, purple sky) | video_20241124_182031 | 59–76 | L → R |
| 3 | 1.80–2.40 | SeaWorld Abu Dhabi | video_20241125_155557 | 45–61 | R → L |
| 4 | 2.40–3.00 | Dubai Frame | video_20241126_103842 | 47–63 | L → R |
| 5 | 3.00–3.60 | Dubai Safari Park | video_20241128_162531 | 49–66 | R → L |
| 6 | 3.60–4.20 | "101" heritage street | video_20241125_150317 | 43–59 | L → R |
| 7 | 4.20–4.80 | Yellow building / tower plaza | video_20241125_105724 | 58–74 | R → L |
| 8 | 4.80–7.77 | Desert sunset finale (walks into the sun, turns to camera) | video_20241126_171319 | 83–171 | L → |

Music: put the first downbeat at 0.00 s. Cuts land on beats 3, 4, 5, 6, 7, 8, 9 and 10
(1.2, 1.8, 2.4, 3.0, 3.6, 4.2 and 4.8 s). Use any 100 BPM track; for 200 BPM, cuts fall on every
second beat.

The locations are not in shooting order. They're ordered so that foot parity and scale match at every
cut. Chronological order breaks the foot alternation.

## Full clip audit (all 26)

| Clip | Location / outfit | Verdict | Why |
|------|-------------------|---------|-----|
| 20241124_111755 | Ferrari World, beige jacket + jeans | **USED** (opening) | Full-frame, clean start on her back. Ends with her greeting a friend, so it's cut before that. |
| 20241124_112048 | Ferrari World concourse | Reject | A man in navy walks in front of her and blocks the subject from 1.8 s. |
| 20241124_112125 | Ferrari World | Alt | Baked-in black side bars (816 px content), so it needs a 1.32× upscale. Crowd and kid in red. |
| 20241124_112246 | Ferrari World | Alt | Same black bars. People in red and blue cross the frame. |
| 20241124_112313 | Ferrari World | Alt (best composition) | Cleanest framing, but the same black bars cost resolution. |
| 20241124_181907 | Hollywood street, black top | Alt | Starts mid-distance, with no close-up on her back. |
| 20241124_181938 | Hollywood street | Alt | More crowd behind her. |
| 20241124_182031 | Hollywood street | **USED** | Cleanest take, good centre line. |
| 20241125_105612 | Yellow plaza, white top + black pants | Alt | Harsh shadow, plain background. |
| 20241125_105724 | Yellow building + tower | **USED** | Strongest background. |
| 20241125_150317 | "101" heritage street | **USED** | Only take; clean. |
| 20241125_155557 | SeaWorld | **USED** | Clean. |
| 20241125_155635 | SeaWorld | Alt | A child in pink runs through the background at ~2 s. |
| 20241126_103842 | Dubai Frame, striped top | **USED** | Wide, clean, centred. |
| 20241126_103953 | Dubai Frame | Alt | Starts mid-distance, camera tilted. |
| 20241126_171245 | Desert sunset | Alt | Lovely sun flare, but she never turns around. |
| 20241126_171319 | Desert sunset | **USED** (finale) | Walks into the sun, turns to camera. |
| 20241126_171353 | Desert | Reject | Camera drifts; she slides off the left edge. |
| 20241126_171415 | Desert, blue hour | Alt | Best pose, but auto-exposure jumps (visible brightness pop) at ~5.5 s. |
| 20241127_092218 | Corniche / flag plaza | Reject | A pedestrian in red walks next to her from 2.5 s; a man crosses in front at 3.3 s. |
| 20241128_162406 | Safari Park | Reject | 1.3 s of her back only, with no walk. |
| 20241128_162421 | Safari Park shop front | Alt | Good; same outfit as the used Safari shot. |
| 20241128_162450 | Safari Park | Reject | Railing in the foreground, 2.4 s only. |
| 20241128_162531 | Dubai Safari Park sign | **USED** | Clean, sign visible. |
| 20241128_162551 | Safari Park | Reject | Her back only, with no walk. |
| 20241128_162602 | Safari Park | Alt (finale option) | Starts mid-distance; long clean turn and pose. |

## How the alignment was verified

1. Pose detection (YOLO11-pose) tracks her body box and ankles on every frame of each candidate take.
2. A periodic gait model fit to the ankle separation finds the heel-strike frames and which foot is
   landing. Fit quality r² is 0.6–0.9; her cadence is 16.5–18.5 frames per step in every clip.
3. A search over in/out points and middle-clip order keeps foot alternation, holds scale within 3% at
   every cut, and caps zoom at 1.42×.
4. Opacity check: `review/cut_overlay_check.jpg` shows each cut as outgoing frame | incoming frame |
   50% blend. Her silhouette overlaps at every cut.

## Known limits

- The push-in tops out at 1.42×, which is mild upscaling from 1080p. It's fine for Reels and TikTok.
  For a sharper result, shoot at 4K next time.
- Ferrari World's best-composed takes (112125, 112246, 112313) have black side bars baked into the
  file. If the camera app has a crop or stabilisation mode that adds them, turn it off.
- The output is silent. Add the music in CapCut, Premiere or Resolve on the 100 BPM grid above.
- `scripts/` reproduces the edit. Paths inside are set for the session that made it.
