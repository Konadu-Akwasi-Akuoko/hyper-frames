"""Default cue recipes baked into every catalog.

This is the curated, video-first SFX palette. Each cue is a *signature* sound:
it pins one handpicked `default_asset` that it reuses across the whole video, and
it declares an `align` mode that decides where the sound lands relative to the
visual:

  align="onset"  — punctuation cues (tick, pop, ding, impact, snap, card-tap).
                   The audible transient lands ON the visual impact frame, biased
                   a hair late so it is never early.
  align="peak"   — anticipatory cues (whoosh, riser). The swell leads in and the
                   PEAK lands on arrival. For MOTION/transitions only.

`default_lead_ms` is a ±tuning knob only (default 0); alignment does the work.
`default_volume` is 0.4 — the fixed house level. It is now informational only:
`tools/sfx-plan` hard-pegs every cue's volume at 0.4 (`PEG_VOLUME`), so this field
no longer varies per cue and a `data-sfx-volume` override is ignored. The `filter`
is a fallback pool used only if an element pins neither `data-sfx-asset` nor
inherits the cue's `default_asset`.

A cue's character comes from what the on-screen beat is *doing* (the verb), never
from a CSS class:
  appears/pops in → pop (or tick)   highlighted/named → ding   lands w/ weight → impact
  slides/travels  → whoosh          builds → riser              freeze/highlight → snap
"""
from __future__ import annotations

from sfx_catalog.core import CueRecipe


def default_cues() -> dict[str, CueRecipe]:
    return {
        # Small UI arrival — a clean light tick.
        "ui-tick": CueRecipe(
            name="ui-tick",
            align="onset",
            default_asset="Mister Horse Free SFX/Click/Mouse Click 01.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "auto_role": "accent",
                "category_in": ["Click", "Tap _ Knock", "Pop", "Beep", "Doink", "Clink", "Blip"],
                "duration_s_max": 0.5,
                "brightness_in": ["bright", "airy"],
            },
        ),
        # A thing pops/fades in — pop-up graphics, list items, icons.
        "pop": CueRecipe(
            name="pop",
            align="onset",
            default_asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "auto_role": "accent",
                "duration_s_max": 0.3,
                "brightness_in": ["warm", "bright"],
            },
        ),
        # Attention called to text / a stat — a bright upward bell.
        "msg-ding": CueRecipe(
            name="msg-ding",
            align="onset",
            default_asset="Mister Horse Free SFX/Rewards/Bells 1 Upward 03.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "category_in": ["Beep", "Rewards", "Clink"],
                "duration_s_max": 0.9,
                "brightness_in": ["airy", "bright"],
            },
        ),
        # Lands with weight / a major point — a clean bass impact.
        "boom": CueRecipe(
            name="boom",
            align="onset",
            default_asset="Mister Horse Free SFX/Bass/Clean Bass Drop 01.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "low_energy_pct_min": 50,
                "peak_time_s_max": 0.25,
            },
        ),
        # Motion / transition — the swell leads into the move (peak-aligned).
        "whoosh": CueRecipe(
            name="whoosh",
            align="peak",
            default_asset="Whooshes/fast woosh 2.mp3",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "auto_role": "transition",
                "duration_s_min": 0.4,
                "duration_s_max": 1.5,
                "attack_time_s_min": 0.1,
            },
        ),
        # Build into a reveal (peak-aligned) — the riser's climax lands on the
        # reveal, the build leading up to it.
        "riser": CueRecipe(
            name="riser",
            align="peak",
            default_asset="Risers/Riser Stop.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "auto_role": "riser",
                "duration_s_min": 1.5,
            },
        ),
        # Freeze-frame / highlight a specific element — a camera shutter.
        "snap": CueRecipe(
            name="snap",
            align="onset",
            default_asset="Mister Horse Free SFX/Click/Camera Shutter Click 01.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "category_in": ["Click"],
                "duration_s_max": 0.4,
                "brightness_in": ["bright", "airy"],
            },
        ),
        # A tile/card taps onto a surface — a soft, dry tap (NOT a keyboard click).
        "card-tap": CueRecipe(
            name="card-tap",
            align="onset",
            default_asset="Mister Horse Free SFX/Tap _ Knock/Single Tap 01.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "category_in": ["Tap _ Knock"],
                "duration_s_max": 0.4,
            },
        ),
        # A light blip — a chip/blip arriving.
        "card-blip": CueRecipe(
            name="card-blip",
            align="onset",
            default_asset="Mister Horse Free SFX/Blip/Synthetic Blip 01.wav",
            default_lead_ms=0,
            default_volume=0.4,
            filter={
                "category_in": ["Pop", "Blip", "Clink"],
                "duration_s_max": 0.4,
                "brightness_in": ["airy", "bright", "warm"],
            },
        ),
    }
