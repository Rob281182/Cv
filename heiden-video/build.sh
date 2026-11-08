#!/usr/bin/env bash
# Build the Heiden Cycle Works homepage intro loop.
#
#   ./build.sh                 -> clean loops for the website (no text baked in)
#   ./build.sh --burn-in       -> also bake the wordmark + headline into the video (for Instagram etc.)
#   ./build.sh --preview       -> fast draft encode, mp4 only
#
# Reads shotlist.txt, looks for each clip in clips/<stem>.<ext>, trims/crops/grades it,
# cuts the shots together, and writes desktop (1920x1080) and mobile (720x1280) mp4 + webm
# plus a poster frame into out/.  Shots with no footage get a labelled placeholder plate.
set -euo pipefail
cd "$(dirname "$0")"

SHOTLIST=${SHOTLIST:-shotlist.txt}
CLIPS=${CLIPS:-clips}
OUT=${OUT:-out}
FPS=25
LOGO=${LOGO:-assets/heiden-wordmark.png}
HEADLINE=${HEADLINE:-Custom carbon bikes, built in Brisbane}
SUBLINE=${SUBLINE:-Carbon tubes and 3D-printed lugs, designed and made to measure by hand.}
HEADFONT=${HEADFONT:-assets/Bricolage-Grotesque.ttf}
SUBFONT=${SUBFONT:-assets/Platypi.ttf}
BURN=0; PREVIEW=0
for a in "$@"; do case "$a" in --burn-in) BURN=1;; --preview) PREVIEW=1;; esac; done

# Cinematic grade: slight contrast lift, crushed blacks, desaturated, soft vignette, fine grain.
GRADE="eq=contrast=1.07:brightness=-0.02:saturation=0.82,curves=all='0/0 0.22/0.18 0.5/0.49 0.78/0.80 1/0.97',vignette=angle=PI/4.6,noise=alls=4:allf=t+u"

mkdir -p "$OUT" build
[ -f "$LOGO" ] || python3 tools/make_placeholders.py --wordmark "$LOGO"

find_clip() { # stem -> path or empty
  local s=$1 f
  for f in "$CLIPS/$s".{mp4,MP4,mov,MOV,m4v,webm,mkv,jpg,JPG,jpeg,JPEG,png,PNG,webp}; do
    [ -f "$f" ] && { echo "$f"; return 0; }
  done
  return 0
}
is_image() { case "${1,,}" in *.jpg|*.jpeg|*.png|*.webp) return 0;; *) return 1;; esac; }

render_variant() { # name W H
  local name=$1 W=$2 H=$3
  local i=0 total=0 missing=0
  local list="build/$name.txt"
  local plates="build/placeholders-$name"
  : > "$list"
  while IFS='|' read -r id stem start dur desc; do
    [[ -z "${id// }" || "$id" =~ ^# ]] && continue
    id=${id// }; stem=${stem// }; start=${start// }; dur=${dur// }
    i=$((i+1)); total=$(echo "$total + $dur" | bc -l)
    local frames; frames=$(python3 -c "print(round($dur*$FPS))")
    local src; src=$(find_clip "$stem")
    local seg="build/$name-$id.mp4"
    if [ -z "$src" ]; then
      [ -d "$plates" ] || python3 tools/make_placeholders.py "$SHOTLIST" "$plates" "$W" "$H" >/dev/null
      src="$plates/$stem.png"; missing=$((missing+1))
      echo "  shot $id: no clip for '$stem' -> placeholder"
    else
      echo "  shot $id: $src"
    fi
    if is_image "$src"; then
      # Slow push-in (odd shots) or slow slide (even shots) on a still, rendered from a 2x upsample for smoothness.
      local zp
      if (( 10#$id % 2 )); then
        zp="zoompan=z='1+0.09*on/$frames':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$frames:s=${W}x${H}:fps=$FPS"
      else
        zp="zoompan=z='1.08':x='(iw-iw/zoom)*(0.3+0.4*on/$frames)':y='ih/2-(ih/zoom/2)':d=$frames:s=${W}x${H}:fps=$FPS"
      fi
      ffmpeg -nostdin -v error -y -i "$src" -vf "scale=$((W*2)):$((H*2)):force_original_aspect_ratio=increase,crop=$((W*2)):$((H*2)),$zp,$GRADE,format=yuv420p" \
        -frames:v "$frames" -c:v libx264 -preset veryfast -crf 14 -an "$seg"
    else
      ffmpeg -nostdin -v error -y -ss "$start" -i "$src" -t "$dur" \
        -vf "fps=$FPS,scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,$GRADE,format=yuv420p" \
        -frames:v "$frames" -c:v libx264 -preset veryfast -crf 14 -an "$seg"
    fi
    echo "file '$name-$id.mp4'" >> "$list"
  done < "$SHOTLIST"

  local fadeout; fadeout=$(python3 -c "print(max(0,$total-0.35))")
  local vf="fade=t=in:st=0:d=0.35,fade=t=out:st=$fadeout:d=0.35"
  local inputs=(-f concat -safe 0 -i "$list")
  local fc=""
  if [ "$BURN" = 1 ]; then
    local lw hs ss hy hl sl nl
    lw=$(python3 -c "print(int($W*(0.36 if $W>$H else 0.62)))")
    hs=$(python3 -c "print(int($H*(0.052 if $W>$H else 0.036)))")
    ss=$(python3 -c "print(int($H*(0.021 if $W>$H else 0.0165)))")
    hy=$(python3 -c "print(int($H*(0.62 if $W>$H else 0.60)))")
    # Wrap the titles for the frame shape (drawtext reads them from files so commas and quotes are safe).
    hl="build/$name-headline.txt"; sl="build/$name-subline.txt"
    python3 -c "import textwrap,sys;print('\n'.join(textwrap.wrap(sys.argv[1],int(sys.argv[2]))),end='')" "$HEADLINE" $([ $W -gt $H ] && echo 60 || echo 20) > "$hl"
    python3 -c "import textwrap,sys;print('\n'.join(textwrap.wrap(sys.argv[1],int(sys.argv[2]))),end='')" "$SUBLINE"  $([ $W -gt $H ] && echo 95 || echo 40) > "$sl"
    nl=$(( $(wc -l < "$hl") + 1 ))
    local sy; sy=$(python3 -c "print(int($hy + $hs*(1.22*$nl + 0.45)))")
    inputs+=(-i "$LOGO")
    fc="[0:v]$vf,drawbox=c=black@0.18:t=fill[v0];[1:v]scale=$lw:-1[l];[v0][l]overlay=(W-w)/2:(H-h)/2-H*0.06:format=auto,\
drawtext=fontfile=$HEADFONT:textfile=$hl:text_align=center:fontsize=$hs:line_spacing=$((hs/8)):fontcolor=white:x=(w-text_w)/2:y=$hy:shadowcolor=black@0.5:shadowx=0:shadowy=2,\
drawtext=fontfile=$SUBFONT:textfile=$sl:text_align=center:fontsize=$ss:line_spacing=$((ss/3)):fontcolor=white@0.9:x=(w-text_w)/2:y=$sy:shadowcolor=black@0.5:shadowx=0:shadowy=1,format=yuv420p[v]"
    vf=""
  fi
  local suffix=""; [ "$BURN" = 1 ] && suffix="-titled"
  local base="$OUT/heiden-home-intro-$name$suffix"
  local x264=(-c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.1 -movflags +faststart -an -r $FPS)
  if [ "$PREVIEW" = 1 ]; then x264+=(-preset veryfast -crf 24); else x264+=(-preset slow -crf 21); fi
  if [ -n "$fc" ]; then
    ffmpeg -nostdin -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[v]" "${x264[@]}" "$base.mp4"
  else
    ffmpeg -nostdin -v error -y "${inputs[@]}" -vf "$vf,format=yuv420p" "${x264[@]}" "$base.mp4"
  fi
  if [ "$PREVIEW" != 1 ]; then
    ffmpeg -nostdin -v error -y -i "$base.mp4" -c:v libvpx-vp9 -b:v 0 -crf 33 -row-mt 1 -deadline good -cpu-used 2 -an "$base.webm"
  fi
  # Poster = first frame after the fade-in
  ffmpeg -nostdin -v error -y -ss 0.4 -i "$base.mp4" -frames:v 1 -q:v 3 "$base-poster.jpg"
  ffmpeg -nostdin -v error -y -ss 0.4 -i "$base.mp4" -frames:v 1 -c:v libwebp -quality 82 "$base-poster.webp" 2>/dev/null || true
  echo "  -> $base.mp4  (${total}s, $i shots, $missing placeholder$([ $missing = 1 ] || echo s))"
}

echo "Desktop 1920x1080"; render_variant desktop 1920 1080
echo "Mobile 720x1280";   render_variant mobile 720 1280
echo "Done. Files in $OUT/"
