/**
 * Ambient drifting floodlight glow. Rendered once near the root so the whole
 * desk feels lit from above. Purely decorative.
 */
export default function FloodlightBg() {
  return (
    <div
      aria-hidden="true"
      className="animate-flood pointer-events-none fixed inset-0 z-0"
      style={{
        background:
          "radial-gradient(38% 46% at 60% -6%, rgba(244,196,48,0.09), transparent 70%)"
      }}
    />
  );
}
