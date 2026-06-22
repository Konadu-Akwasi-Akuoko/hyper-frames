/** Horizontal level bar — the track IS the full teal→red ramp; a mask hides the
 *  unachieved (1 - progress) portion, so full progress genuinely reaches red.
 *  Same meter law as the wire, laid down (spec §10.1). */
export default function DeskMeter({ progress }: { progress: number }) {
  const mask = Math.max(0, Math.min(100, (1 - progress) * 100));
  return (
    <div className="desk-meter">
      <span className="mask" style={{ width: `${mask}%` }} />
    </div>
  );
}
