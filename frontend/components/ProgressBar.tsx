import * as React from "react";
import { cn } from "@/lib/utils";
interface ProgressBarProps extends React.HTMLAttributes<HTMLDivElement> {
progress: number;
variant?: "default" | "authentic" | "synthetic" | "inconclusive";
}
export function ProgressBar({ progress, variant = "default", className, ...props }: ProgressBarProps) {
const clampedProgress = Math.max(0, Math.min(100, progress));
const variants = {
default: "bg-accent",
authentic: "bg-signal-authentic",
synthetic: "bg-signal-synthetic",
inconclusive: "bg-signal-inconclusive",
};
return (
<div
className={cn("w-full h-[2px] bg-border-subtle overflow-hidden", className)}
{...props}
>
<div
className={cn("h-full transition-all duration-300 ease-out", variants[variant])}
style={{ width: `${clampedProgress}%` }}
/>
</div>
);
}
