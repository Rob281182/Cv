# Heiden Cycle Works — homepage intro loop

A production kit for a homepage video in the style of the [Simpatico Bikes](https://simpaticobikes.com/) intro:
a short, muted, looping film that fills the screen, with the logo and a one-line headline sitting over it,
and the rest of the page scrolling up over the top of it.

**Status:** the pipeline, page and timing are done. The footage is not. Every shot currently renders as a
labelled grey placeholder because no Heiden Cycle Works photos or video exist in this repo, your Google Drive
or your Gmail. Shoot the ten shots below, drop them in `clips/`, run `./build.sh`, and the finished loops
land in `out/`.

## What the Simpatico video actually is (so we match it)

| | Simpatico | This kit |
|---|---|---|
| Length | 9.64 s, then loops | 9.64 s, loops |
| Frame rate | 25 fps | 25 fps |
| Sound | none (muted, autoplay) | none |
| Desktop file | 1920×1080 mp4 + webm, ~4 MB | same |
| Mobile file | 720×1280 vertical mp4 + webm | same |
| Shots | 10 hard cuts: 4 studio shots of the bike on black with one hard rim light, 1 rider silhouette on a red-lit wall, 5 riding shots on forest gravel, low camera | same structure, see `shotlist.txt` |
| Look | dark, desaturated, crushed blacks, light film grain | applied automatically by `build.sh` |
| Overlay | white logo centred, headline + one line of copy below, soft dark gradient top and bottom, pause button bottom-right | `web/index.html` |
| Text in the video file | none, all overlaid in HTML | none by default; `--burn-in` bakes it in for Instagram etc. |

## Folder

```
heiden-video/
  shotlist.txt         the ten shots, their order, length and what to film
  clips/               put your footage here, named 01-studio-profile.mov, 02-studio-downtube.mp4, ...
  build.sh             turns clips/ into the finished loops in out/
  out/                 heiden-home-intro-desktop.{mp4,webm}, -mobile.{mp4,webm}, poster frames,
                       and -titled versions with the logo and headline baked in
  web/index.html       the hero section, ready to drop into a site
  assets/              wordmark (placeholder, replace it), Bricolage Grotesque + Platypi fonts (OFL)
  tools/               placeholder generator used by build.sh
  preview/             contact sheets of the current render
```

## Shooting the ten shots

Shoot everything on a phone at 4K, 25 fps (or 24), in the "Cinematic" or normal video mode with exposure
locked. Shoot a touch underexposed; the grade crushes the blacks anyway. Each shot only needs to be
one second long in the edit, so record 5 to 10 seconds of each and the build takes the first second (set the
start offset in `shotlist.txt` to pick a different second).

**Studio shots (01 to 04).** A garage or room at night, every light off, matt black backdrop or just
distance behind the bike, one hard light (a work lamp, torch or bare bulb) placed behind and to one side
of the bike so it skims along the tubes. Phone on a tripod or propped on a box. For the moving shots,
slide the phone slowly along a table edge or push it on a skateboard. Shot 02 should land on a 3D-printed
lug catching the light: that is the thing nobody else has.

**Silhouette (05).** A rider in the drops in front of a wall lit by a single coloured light (a coloured
bulb or a phone torch through cellophane). Simpatico uses red; pick the Heiden brand colour. Expose for
the wall so the rider goes fully black.

**Riding shots (06 to 10).** Dawn or late afternoon on forest gravel: Mount Coot-tha, Gap Creek, Daisy Hill
or similar. Phone low, on or near the ground, locked off; the rider does the same pass four or five times.
Shot 10 is the front wheel passing within a hand's width of the lens.

Stills work too: a JPG or PNG in `clips/` gets a slow push-in or slide automatically, so a good studio
photo can stand in for a video shot.

## Building

```bash
cd heiden-video
./build.sh              # clean loops for the website -> out/
./build.sh --burn-in    # also write *-titled.* with the logo and headline baked in
./build.sh --preview    # fast draft, mp4 only
```

Needs `ffmpeg` (with libx264 and libvpx-vp9) and Python 3 with Pillow. Override the copy without editing
the script:

```bash
HEADLINE="Made to measure. Made in Brisbane." SUBLINE="Carbon frames with 3D-printed lugs." ./build.sh --burn-in
```

Grade, durations and the fade at the loop seam live at the top of `build.sh`.

## Using it on the site

`web/index.html` is the hero section with the same behaviour as Simpatico's: sticky full-screen video,
poster image shown until the video can play, vertical cut on phones, pause button, and a still poster for
people who have reduced motion turned on. It references `../out/` and `../assets/`; copy those folders
alongside it, or change the four `data-*` paths and the poster paths at the top of the section.

## Before this is real

1. Replace `assets/heiden-wordmark.png` with the actual Heiden Cycle Works logo (white on transparent).
2. Set `--accent` in `web/index.html` to the brand colour.
3. Check the headline and subline wording; both are drawn from the facts in the CV.
