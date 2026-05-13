"""Default cue recipes baked into every catalog.

A cue's filter is a flat dict; each key is a filter operator applied against
CatalogEntry fields. Operators:
  <field>            — exact match
  <field>_min        — entry[field] >= value
  <field>_max        — entry[field] <= value
  <field>_in         — entry[field] in value
"""
from __future__ import annotations

from sfx_catalog.core import CueRecipe


def default_cues() -> dict[str, CueRecipe]:
    return {
        "ui-tick": CueRecipe(
            name="ui-tick",
            default_lead_ms=-50,
            default_volume=0.8,
            filter={
                "auto_role": "accent",
                "category_in": ["Click", "Tap _ Knock", "Pop", "Beep", "Doink", "Clink", "Blip"],
                "duration_s_max": 0.5,
                "brightness_in": ["bright", "airy"],
            },
        ),
        "whoosh": CueRecipe(
            name="whoosh",
            default_lead_ms=-150,
            default_volume=0.9,
            filter={
                "auto_role": "transition",
                "duration_s_min": 0.4,
                "duration_s_max": 1.5,
                "attack_time_s_min": 0.1,
            },
        ),
        "boom": CueRecipe(
            name="boom",
            default_lead_ms=0,
            default_volume=1.0,
            filter={
                "auto_role": "impact",
                "low_energy_pct_min": 50,
                "peak_time_s_max": 0.2,
            },
        ),
        "riser": CueRecipe(
            name="riser",
            default_lead_ms=None,
            default_volume=0.85,
            filter={
                "auto_role": "riser",
                "duration_s_min": 1.5,
            },
        ),
        "pop": CueRecipe(
            name="pop",
            default_lead_ms=-50,
            default_volume=0.8,
            filter={
                "auto_role": "accent",
                "duration_s_max": 0.3,
                "brightness_in": ["warm", "bright"],
            },
        ),
        "msg-ding": CueRecipe(
            name="msg-ding",
            default_lead_ms=-50,
            default_volume=0.7,
            filter={
                "auto_role": "accent",
                "category_in": ["Beep"],
                "duration_s_max": 0.6,
                "brightness_in": ["airy", "bright"],
            },
        ),
        "card-tap": CueRecipe(
            name="card-tap",
            default_lead_ms=-50,
            default_volume=0.8,
            filter={
                "auto_role": "accent",
                "category_in": ["Click", "Tap _ Knock"],
                "duration_s_max": 0.4,
            },
        ),
        "card-blip": CueRecipe(
            name="card-blip",
            default_lead_ms=-50,
            default_volume=0.65,
            filter={
                "auto_role": "accent",
                "category_in": ["Pop", "Blip", "Clink"],
                "duration_s_max": 0.4,
                "brightness_in": ["airy", "bright", "warm"],
            },
        ),
    }
