import * as React from "react";
import { cn } from "@/lib/utils";
export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
variant?: "default" | "authentic" | "synthetic" | "inconclusive" | "outline";
}
export function Badge({ className, variant = "default", ...props }: BadgeProps) {
const variants = {
default: "bg-border-subtle text-text-primary",
authentic: "bg-signal-authentic/20 text-signal-authentic border border-signal-authentic/30",
synthetic: "bg-signal-synthetic/20 text-signal-synthetic border border-signal-synthetic/30",
inconclusive: "bg-signal-inconclusive/20 text-signal-inconclusive border border-signal-inconclusive/30",
outline: "border border-border-subtle text-text-secondary",
};
return (
<div
className={cn(
"inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-sm",
variants[variant],
className
)}
{...props}
/>
);
}
