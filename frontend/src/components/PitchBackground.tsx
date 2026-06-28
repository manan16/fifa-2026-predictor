import { ReactNode } from "react";

export default function PitchBackground({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`relative overflow-hidden bg-stadium text-slate-100 ${className}`}
      style={{
        backgroundImage:
          "radial-gradient(circle at 50% 0%, rgba(250,204,21,0.14), transparent 28rem), radial-gradient(circle at 50% 55%, rgba(22,163,74,0.16), transparent 34rem), linear-gradient(135deg, #07111F 0%, #064E3B 55%, #07111F 100%)"
      }}
    >
      <div
        className="pointer-events-none absolute inset-0 z-0 opacity-35"
        style={{
          backgroundImage:
            "linear-gradient(90deg, rgba(248,250,252,0.035) 1px, transparent 1px), linear-gradient(0deg, rgba(248,250,252,0.03) 1px, transparent 1px)",
          backgroundSize: "64px 64px"
        }}
      />
      <div className="pointer-events-none absolute inset-x-[8%] top-10 z-0 h-[calc(100%-5rem)] rounded-[48px] border border-white/5" />
      <div className="pointer-events-none absolute left-1/2 top-1/2 z-0 h-52 w-52 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/5" />
      <div className="pointer-events-none absolute left-1/2 top-0 z-0 h-full border-l border-white/5" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
