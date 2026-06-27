import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

export function Card({ children, className = "" }: CardProps) {
  return (
    <section
      className={`rounded-lg border border-line bg-panel shadow-xl shadow-black/20 ${className}`}
    >
      {children}
    </section>
  );
}

export function CardHeader({ children, className = "" }: CardProps) {
  return (
    <div
      className={`border-b border-line px-5 py-4 ${className}`}
      data-dashboard-drag-handle
    >
      {children}
    </div>
  );
}

export function CardContent({ children, className = "" }: CardProps) {
  return <div className={`px-5 py-5 ${className}`}>{children}</div>;
}
