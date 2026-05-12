// Border beam motion kit.
//
// Tweens the --beam-angle CSS custom property on a .border-beam element.
// Wire into any GSAP timeline:
//
//   import { spinBorderBeam } from "./design-catalog/border-beam/motion.js";
//   spinBorderBeam(tl, "#my-card", { at: 4.2, duration: 9, repeat: 1 });
//
// Defaults: 9s per lap, one repeat (= 2 laps total), linear ease so the
// comet glides at constant angular velocity.

export function spinBorderBeam(tl, target, opts = {}) {
  const { at = 0, duration = 9, repeat = 1, ease = "none" } = opts;
  tl.to(target, { "--beam-angle": "360deg", duration, ease, repeat }, at);
}
