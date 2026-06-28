import { ReactNode } from "react";

export default function AnimatedPage({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`animate-page-in ${className}`}>{children}</div>;
}

