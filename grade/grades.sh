#!/usr/bin/env bash
# Single source of truth for the two creative grades (color only, LUT-bakeable).
# Sourced by bake + render scripts. Grain is NOT here — it is a render-only stage.

# HDR HLG -> SDR Rec709 front stage (libplacebo, deterministic).
export VK_ICD_FILENAMES=/opt/homebrew/etc/vulkan/icd.d/MoltenVK_icd.json
PLACEBO="libplacebo=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv:tonemapping=bt.2390:gamut_mode=perceptual:peak_detect=false"

# --- Variant A: ref1 soft daylight (v7 — teal in shadows only, clean neutral midtones) ---
A_VF="curves=all='0/0 0.22/0.20 0.5/0.5 0.78/0.76 0.9/0.85 1/0.90',curves=r='0/0 0.3/0.24 0.85/0.80 1/0.95':b='0/0.03 0.5/0.5 1/1',colorbalance=rs=-0.10:gs=0.03:bs=0.06:rm=-0.02:gm=0.01:rh=-0.02:gh=0.01:bh=0.02,eq=saturation=0.86:contrast=1.03"
A_GRAIN="noise=alls=8:allf=t+u"

# --- Variant B: ref2 moody studio ---
B_VF="curves=all='0/0 0.1/0.035 0.5/0.5 0.9/0.95 1/1',curves=r='0/0 0.25/0.155 0.6/0.55 1/1':b='0/0.06 0.5/0.5 1/0.98',colorbalance=rs=-0.16:gs=0.05:bs=0.12:rm=-0.06:rh=0.08:bh=-0.08,eq=saturation=0.72:contrast=1.14"
