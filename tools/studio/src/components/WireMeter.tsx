import type { Lean } from "../format";

/** Vertical 5-segment signal meter — fill height = rationale lean, colored
 *  along the shared cold→hot ramp. One meter law (spec §10.1). */
export default function WireMeter({ lean }: { lean: Lean }) {
  return (
    <div className="wire-meter" data-lean={lean}>
      <i />
      <i />
      <i />
      <i />
      <i />
    </div>
  );
}
