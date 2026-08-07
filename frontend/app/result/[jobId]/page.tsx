"use client";
import { use, useEffect, useState } from "react";
import { useFullResult } from "@/lib/hooks";
import { Card } from "@/components/Card";
import { Badge } from "@/components/Badge";
import { FrameStrip } from "@/components/FrameStrip";
import { AlertTriangle, CheckCircle2, HelpCircle, Download, Activity, Cpu, Scan, Layers } from "lucide-react";
import { Button } from "@/components/Button";
import { formatDuration } from "@/lib/utils";
import { motion } from "framer-motion";

export default function ResultPage(props: { params: Promise<{ jobId: string }> }) {
  const params = use(props.params);
  const { data: result, isLoading, isError } = useFullResult(params.jobId);
  const [score, setScore] = useState(0);

  useEffect(() => {
    if (result) {
      setTimeout(() => setScore(result.confidence), 300);
    }
  }, [result]);

  if (isLoading) {
    return (
      <div className="flex-grow flex items-center justify-center relative overflow-hidden">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
          <Scan className="w-12 h-12 text-accent opacity-50" />
        </motion.div>
        <div className="absolute font-mono text-xs text-accent mt-20">Analyzing Data...</div>
      </div>
    );
  }

  if (isError || !result) {
    return (
      <div className="container mx-auto px-6 py-24 flex justify-center text-synthetic font-mono text-sm">
        Error loading report. Please try again.
      </div>
    );
  }

  const isSynthetic = result.verdict === "likely_ai_generated";
  const isAuthentic = result.verdict === "likely_authentic";
  const variantColor = isSynthetic ? "#EF4444" : isAuthentic ? "#4ADE80" : "#F59E0B";
  const variantClass = isSynthetic ? "text-synthetic" : isAuthentic ? "text-authentic" : "text-inconclusive";
  const verdictText = isSynthetic ? "HIGH RISK OF MANIPULATION" : isAuthentic ? "AUTHENTIC FOOTAGE" : "INCONCLUSIVE";
  const Icon = isSynthetic ? AlertTriangle : isAuthentic ? CheckCircle2 : HelpCircle;

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6 } },
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="flex-grow flex flex-col relative">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-accent/10 blur-[150px] rounded-full pointer-events-none" />
      
      <div className="container mx-auto px-6 py-16 flex-grow z-10">
        
        {/* Top Header & Massive Gauge */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 mb-16 items-center">
          <motion.div variants={item} className="flex flex-col gap-6">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border bg-black/20 font-mono text-sm uppercase tracking-widest ${isSynthetic ? 'border-synthetic/30 text-synthetic' : isAuthentic ? 'border-authentic/30 text-authentic' : 'border-inconclusive/30 text-inconclusive'}`}>
              <Icon className="w-4 h-4" />
              <span>{verdictText}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight leading-tight">
              Forensic Analysis Complete.
            </h1>
            <p className="text-text-secondary text-lg max-w-md">
              {isSynthetic ? "Our multi-modal engines have detected strong anomalies indicative of AI generation or deepfake manipulation." : "No significant synthetic artifacts were found. The footage exhibits natural spatial and temporal consistency."}
            </p>
            <div className="pt-4 flex gap-4">
              <Button onClick={() => window.open(`http://localhost:8000/api/v1/results/${params.jobId}/export`, '_blank')}>
                <Download className="w-4 h-4 mr-2" /> Download Full Report
              </Button>
            </div>
          </motion.div>

          <motion.div variants={item} className="flex justify-center relative">
            <div className="relative w-72 h-72 flex items-center justify-center">
              {/* SVG Circular Gauge */}
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* Background Track */}
                <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
                {/* Animated Value */}
                <motion.circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={variantColor}
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray="283"
                  initial={{ strokeDashoffset: 283 }}
                  animate={{ strokeDashoffset: 283 - (283 * score) / 100 }}
                  transition={{ duration: 2, ease: "easeOut", delay: 0.5 }}
                />
              </svg>
              {/* Center Text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-6xl font-bold font-mono tracking-tighter ${variantClass}`}>
                  {score.toFixed(1)}<span className="text-3xl">%</span>
                </span>
                <span className="text-xs text-text-secondary uppercase tracking-widest mt-2">AI Probability</span>
              </div>
              
              {/* Outer Glow */}
              <motion.div 
                animate={{ scale: [1, 1.05, 1], opacity: [0.5, 0.8, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
                className={`absolute inset-0 rounded-full blur-2xl -z-10 ${isSynthetic ? 'bg-synthetic/20' : isAuthentic ? 'bg-authentic/20' : 'bg-inconclusive/20'}`}
              />
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          <motion.div variants={item} className="lg:col-span-2 flex flex-col gap-6">
            <h2 className="text-2xl font-semibold text-white">Forensic Evidence</h2>
            <Card className="flex flex-col gap-4">
              <ul className="space-y-4">
                {result.explanation_bullets.map((bullet, idx) => (
                  <motion.li 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1 + (idx * 0.2) }}
                    key={idx} 
                    className="flex gap-4 items-start"
                  >
                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent flex-shrink-0 shadow-[0_0_8px_rgba(108,99,255,0.8)]" />
                    <span className="text-text-secondary leading-relaxed text-sm md:text-base">{bullet}</span>
                  </motion.li>
                ))}
              </ul>
            </Card>

            <h2 className="text-2xl font-semibold text-white mt-8">Signal Streams Breakdown</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Spatial CNN", val: result.stream_breakdown.spatial, icon: Layers },
                { label: "Frequency FFT", val: result.stream_breakdown.frequency, icon: Activity },
                { label: "Temporal Motion", val: result.stream_breakdown.temporal, icon: Scan },
                { label: "Compression", val: result.stream_breakdown.compression, icon: Cpu }
              ].map((stream, idx) => (
                <Card key={idx} className="p-5 flex flex-col gap-3 group">
                  <div className="flex items-center gap-2 text-sm text-text-secondary">
                    <stream.icon className="w-4 h-4 group-hover:text-accent transition-colors" />
                    {stream.label}
                  </div>
                  <div className="font-mono text-2xl text-white font-medium">{stream.val.toFixed(1)}%</div>
                  <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden mt-1">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${stream.val}%` }}
                      transition={{ duration: 1.5, delay: 1.5 }}
                      className="h-full bg-accent-alt rounded-full"
                    />
                  </div>
                </Card>
              ))}
            </div>
          </motion.div>

          <motion.div variants={item} className="flex flex-col gap-6">
            <h2 className="text-2xl font-semibold text-white">Metadata</h2>
            <Card className="flex flex-col gap-6">
              {[
                { label: "Job ID", val: params.jobId, break: true },
                { label: "Filename", val: result.filename, break: true },
                { label: "Processing Time", val: `${result.processing_time_ms} ms` },
                { label: "Frames Extracted", val: result.frames_analyzed },
                { label: "Faces Tracked", val: `${result.faces_detected_in} frames` },
                { label: "Resolution", val: `${result.video.width} × ${result.video.height}` },
                { label: "Duration", val: formatDuration(result.video.duration_seconds) },
                { label: "Model Engine", val: result.model_version }
              ].map((meta, idx) => (
                <div key={idx} className="flex flex-col gap-1 border-b border-white/5 pb-4 last:border-0 last:pb-0">
                  <span className="text-xs text-text-secondary uppercase tracking-widest">{meta.label}</span>
                  <span className={`font-mono text-sm text-white ${meta.break ? 'break-all' : ''}`}>{meta.val}</span>
                </div>
              ))}
            </Card>
          </motion.div>
        </div>
      </div>

      <motion.div variants={item} className="w-full mt-auto bg-black/40 border-t border-border-subtle pt-8 pb-12">
        <div className="container mx-auto px-6 mb-6">
          <h2 className="text-xl font-semibold text-white">Timeline Analysis</h2>
          <p className="text-sm text-text-secondary mt-1">Frame-by-frame deepfake probability breakdown.</p>
        </div>
        <FrameStrip jobId={params.jobId} />
      </motion.div>
    </motion.div>
  );
}
