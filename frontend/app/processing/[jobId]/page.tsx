"use client";
import { useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { useJobWebSocket } from "@/lib/hooks";
import { Check, CircleDashed } from "lucide-react";
import { Card } from "@/components/Card";
const PIPELINE_STAGES = [
{ id: "pending", label: "Initialization" },
{ id: "uploading", label: "Uploading File" },
{ id: "uploaded", label: "Upload Complete" },
{ id: "validating", label: "Validating Format" },
{ id: "extracting_frames", label: "Extracting Frames" },
{ id: "detecting_faces", label: "Detecting Faces" },
{ id: "running_inference", label: "Running Detection Ensemble" },
{ id: "aggregating", label: "Generating Report" },
{ id: "completed", label: "Analysis Complete" },
];
export default function ProcessingPage(props: { params: Promise<{ jobId: string }> }) {
const params = use(props.params);
const router = useRouter();
const { status, isConnected } = useJobWebSocket(params.jobId);
useEffect(() => {
if (status?.stage === "completed") {
const timer = setTimeout(() => {
router.push(`/result/${params.jobId}`);
}, 500);
return () => clearTimeout(timer);
}
}, [status?.stage, params.jobId, router]);
const currentStageIndex = PIPELINE_STAGES.findIndex((s) => s.id === status?.stage) || 0;
const isFailed = status?.stage === "failed";
return (
<div className="container mx-auto px-6 py-24 flex-grow flex flex-col justify-center items-center">
<div className="w-full max-w-lg">
<h1 className="text-3xl font-medium text-text-primary mb-2">Analyzing Footage</h1>
<p className="text-text-secondary font-mono text-xs mb-12">JOB ID: {params.jobId}</p>
{isFailed ? (
<Card className="border-signal-synthetic/30 bg-signal-synthetic/10">
<h3 className="text-signal-synthetic font-medium mb-2">Analysis Failed</h3>
<p className="text-text-secondary font-mono text-sm">{status.error_message}</p>
</Card>
) : (
<div className="flex flex-col gap-6 pl-2">
{PIPELINE_STAGES.map((stage, idx) => {
const isPast = idx < currentStageIndex;
const isCurrent = idx === currentStageIndex;
const isFuture = idx > currentStageIndex;
return (
<div key={stage.id} className="flex items-center gap-4">
<div className="w-6 h-6 flex items-center justify-center shrink-0">
{isPast ? (
<Check className="w-5 h-5 text-signal-authentic" />
) : isCurrent ? (
<CircleDashed className="w-5 h-5 text-accent animate-spin" style={{ animationDuration: '3s' }} />
) : (
<div className="w-2 h-2 rounded-full bg-border-subtle" />
)}
</div>
<div className="flex flex-col">
<span
className={`font-medium ${
isPast
? "text-text-secondary"
: isCurrent
? "text-text-primary"
: "text-border-subtle"
}`}
>
{stage.label}
</span>
{isCurrent && stage.id === "running_inference" && status?.stage_progress !== undefined && (
<span className="text-xs font-mono text-text-secondary mt-1">
{(status.stage_progress * 100).toFixed(1)}% complete
</span>
)}
</div>
</div>
);
})}
</div>
)}
{!isConnected && !isFailed && status?.stage !== "completed" && (
<p className="text-xs text-text-secondary mt-8 italic">
Reconnecting to live updates...
</p>
)}
</div>
</div>
);
}
