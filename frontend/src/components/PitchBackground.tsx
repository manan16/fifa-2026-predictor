import { ReactNode } from "react";

export default function PitchBackground({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`relative overflow-hidden bg-stadium text-white ${className}`}
      style={{
        backgroundImage:
          "radial-gradient(circle at 50% 0%, rgba(250,204,21,0.18), transparent 28rem), radial-gradient(circle at 50% 55%, rgba(22,163,74,0.18), transparent 34rem), linear-gradient(90deg, rgba(248,250,252,0.035) 1px, transparent 1px), linear-gradient(0deg, rgba(248,250,252,0.03) 1px, transparent 1px), linear-gradient(135deg, #07111F 0%, #064E3B 55%, #07111F 100%)",
        backgroundSize: "auto, auto, 56px 56px, 56px 56px, auto"
      }}
    >
      <div className="pointer-events-none absolute inset-x-[8%] top-10 h-[calc(100%-5rem)] rounded-[48px] border border-line/10" />
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-52 w-52 -translate-x-1/2 -translate-y-1/2 rounded-full border border-line/10" />
      <div className="pointer-events-none absolute left-1/2 top-0 h-full border-l border-line/10" />
      <div className="relative">{children}</div>
    </div>
  );
}

