import type { ReactNode } from "react";
import { Card, CardContent, CardHeader } from "./ui/card";

type DashboardCardProps = {
  title: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function DashboardCard({
  title,
  eyebrow,
  action,
  children,
  className = ""
}: DashboardCardProps) {
  return (
    <Card className={`min-h-[260px] ${className}`}>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          {eyebrow ? <p className="text-xs font-medium uppercase text-cobalt">{eyebrow}</p> : null}
          <h2 className="mt-1 text-lg font-semibold text-ink">{title}</h2>
        </div>
        {action}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
