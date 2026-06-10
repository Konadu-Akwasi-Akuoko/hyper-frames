# Face compositing — the Specimen still

How to turn a user-supplied source image into the right-bled, rim-lit cutout
that anchors the Specimen signature. The face is the emotional payload; the
base + mono tell + layout + pointer carry the brand. Get the cutout edge clean
and the rim matched to the accent, and the still reads as composited-with-craft
rather than pasted-on.

Load this at the compositing step, whenever a variant uses a face.

## Division of labor (standing rule)

**The user supplies and credits the source image. We composite it.** Cut out,
defringe/despill, bleed, rim-light, and place — never source third-party
copyrighted imagery ourselves. If no usable source is on disk, ask the user for
one (and for its credit) before doing any compositing work. A composite can only
be as good as its source; do not try to rescue an unfixable one (see below).

## Source-image requirements

A usable Specimen source is:

- **High-res** — ideally ≥1000 px on the bled dimension. The cutout sits at
  `height: 760` bled to the right edge; a low-res still softens and the rim
  exaggerates the mush.
- **One clear, legible emotion** that matches the headline's beat. The face is
  the reaction; a weary or ambiguous expression reads as nothing at feed size.
- **A clean, keyable background** — a simple/even backdrop so the subject cuts
  cleanly, or a source that is already a transparent PNG. A busy or color-matched
  background (subject's clothing the same hue as the wall) defeats the matte.

No compositing pass fixes a wrong-emotion **and** un-keyable **and** low-res
source at once. When all three are wrong, the answer is a different source image,
not more ImageMagick. Tell the user; do not ship a 4/10 still.

## Cutout

Remove the background with HyperFrames media:

```bash
npx hyperframes remove-background <in> -o cutout.png
```

This runs `u2net_human_seg`. On first use it downloads a ~168 MB model — run it
directly (not piped into another command), confirm the model finishes, and
confirm `cutout.png` actually exists and has non-trivial size before continuing.
A hung download silently produces an empty or missing file, and the face will
simply not render.

## Defringe / despill — the biggest technical win

`remove-background` leaves a **semi-transparent matte fringe** on the edges that
carries the *original* background's color. On the Specimen's green-tinted
near-black base this fringe reads as a glowing **sticker outline** — the single
most "this looks amateur" tell, and a strict QA pass fails on it every time.

**CSS glow does NOT fix a matte fringe.** The fringe is baked into the cutout's
alpha edge; no `.face` filter or `.face-glow` disc removes it. Worse, a strong
glow *adds* a fake keyline on top of the fringe. Fix the PNG itself with
ImageMagick before placing it.

### Defringe — erode the alpha to cut the fringe off

The default pass. Erodes the alpha channel inward so the colored fringe pixels
fall outside the mask:

```bash
magick in.png \( +clone -alpha extract -morphology Erode Disk:1.5 -blur 0x0.6 \) \
  -alpha off -compose CopyOpacity -composite out.png
```

A clean cutout (even backdrop, dark hair, strong subject/background separation)
usually passes on this single `Disk:1.5` pass.

### Despill — when a *colored* halo persists

The hard case is a **colored** halo that survives the defringe — blonde hair or
red/warm cloth shot on a light background is the worst offender. Erode harder
**and** darken + desaturate the edge ring so residual warm pixels sink into the
dark base instead of ringing against it:

```bash
magick in.png \( +clone -alpha extract -morphology Erode Disk:2.5 -blur 0x0.7 \) \
  -alpha off -compose CopyOpacity -composite t1.png
magick t1.png -alpha extract a.png
magick a.png -morphology Erode Disk:6 inner.png
magick a.png inner.png -compose Minus -composite ring.png      # ~6px edge ring
magick t1.png -modulate 32,22 dark.png                          # brightness 32%, sat 22%
magick t1.png dark.png ring.png -composite -alpha set a.png -compose CopyOpacity -composite out.png
```

For a milder warm halo, `-modulate 52,35` over a `Disk:4` ring is enough — start
mild and escalate only if the halo survives. The despill pass is what takes a
blonde/warm cutout from a halo-failing QA score to a clean ship.

Do not over-erode chasing a reviewer: when the "halo" is the subject's own hair
color naturally fading into the dark base, it is a property of the source, not a
fringe. Crop-zoom the edge yourself to tell the difference before eroding further
— mutilating the silhouette is worse than a faint, honest edge.

## Placement and fit

Markup: `.face-wrap` (absolute, bled to the right edge) contains `.face-glow`
plus the cutout `<img class="face">`. The cutout is `height: 760` with
`object-position: bottom right`.

**Use `object-fit: contain`, never `cover`.** `cover` in a fixed
`overflow: hidden` box zooms into the opaque center of the cutout and crops away
the transparent border, so the subject re-reads as a filled rectangular photo
with a hard edge — re-introducing the exact rectangle the cutout was meant to
dissolve. `contain` (height-based, bled to the edge) lets the alpha edge do the
separation.

Text sits left, face bleeds right; they do not overlap, so **no fade/scrim panel
is needed between them**. A gradient scrim's left box edge becomes a hard
vertical line through the canvas — the transparent cutout's own alpha edge plus
the rim does all the separation. Do not add one.

## Rim-light tuning

The rim-light highlight is desirable — it lifts the subject off the base. But it
has to be a soft, diffuse glow, and it has to **match the accent**.

- **Too strong = sticker outline.** A tight, uniform, bright keyline tracing the
  whole silhouette reads as a cheap cutout. Avoid hard `drop-shadow(0 0 1px
  white)`-style keylines.
- **Right = a soft halo that fades, plus a dark cast shadow for depth.** The
  proven `.face` filter shape:

  ```css
  filter: saturate(0.84) contrast(1.14) brightness(1.05)
          drop-shadow(0 0 10px rgba(<accent-rgb>, 0.26))   /* soft halo, accent-matched */
          drop-shadow(-18px 12px 30px rgba(0,0,0,0.55));    /* dark cast shadow = depth */
  ```

- **Match the rim color to the accent**, not to a fixed blue. The `.face-glow`
  disc and the halo `drop-shadow` should carry the variant's accent hue
  (`var(--accent)` for the disc; the accent's RGB in the halo `drop-shadow`).
  A cool glow behind a warm subject *rings* badly; a glow matched to the accent
  reads as deliberate lighting.

### `.warm` — kill the disc for warm/blonde subjects

For blonde or warm-toned subjects, the `.face-glow` disc rings against the
subject's own warm edge no matter what hue it is. Add the `.warm` class to
`.thumbnail`: it removes the `.face-glow` disc entirely and lets the rim
`drop-shadow` plus the dark cast shadow do the separation alone. Use `.warm`
whenever the disc fights the subject; keep the disc for cool/dark subjects where
it cleanly lifts them off the base.

## Self-verification

After placing and rendering, **look at the PNG yourself** before reporting done,
and crop-zoom the risky edge to inspect the cutout at pixel scale:

```bash
magick thumb.png -crop 420x420+540+20 +repage zoom.png   # then read zoom.png
```

Highest-risk item, every time: **cutout/edge artifacts** — any matte fringe,
sticker outline, colored halo, hard rectangular seam, or hard vertical line. If
any of those survive, go back to the defringe/despill pass (or drop the scrim
panel / switch `cover` to `contain`); a CSS tweak will not fix a baked-in edge.
Then confirm the rim is soft, accent-matched, and natural — present, not a
keyline.
