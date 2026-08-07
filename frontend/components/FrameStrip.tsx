"use client";
import { useFrames } from "@/lib/hooks";
export function FrameStrip({ jobId }: { jobId: string }) {
const { data, isLoading } = useFrames(jobId);
if (isLoading) {
return <div className="h-24 bg-border-subtle/20 animate-pulse border-y border-border-subtle"></div>;
}
if (!data?.frames || data.frames.length === 0) {
return null;
}
return (
<div className="w-full overflow-x-auto border-y border-border-subtle bg-bg-surface no-scrollbar">
<div className="flex p-4 gap-2 w-max">
{data.frames.map((frame) => {
const isSuspicious = frame.fusion_score > 0.65;
return (
<div
key={frame.frame_index}
className={`relative flex-shrink-0 w-32 aspect-video border transition-colors ${
isSuspicious ? "border-signal-synthetic" : "border-border-subtle hover:border-text-secondary"
}`}
>
<img
src={frame.frame_url}
alt={`Frame ${frame.frame_index}`}
className="w-full h-full object-cover"
loading="lazy"
/>
<div className="absolute bottom-0 left-0 right-0 bg-bg-primary/80 backdrop-blur-sm p-1 flex justify-between items-center border-t border-border-subtle/50">
<span className="text-[10px] font-mono text-text-secondary">{frame.timestamp_seconds.toFixed(2)}s</span>
<span
className={`text-[10px] font-mono ${
isSuspicious ? "text-signal-synthetic" : "text-text-primary"
}`}
>
{(frame.fusion_score * 100).toFixed(0)}%
</span>
</div>
</div>
);
})}
</div>
</div>
);
}
