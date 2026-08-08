"use client";

import React from "react";
import Link from "next/link";
import { Card } from "@/components/Card";
import { JobStatusResponse } from "@/lib/types";
import { formatDuration } from "@/lib/utils";
import { ArrowRight, ShieldAlert, CheckCircle, Clock } from "lucide-react";

export function EvidenceCard({ job }: { job: JobStatusResponse }) {
  const isVerified = job.investigation_status === "Verified";
  const isSuspected = job.investigation_status === "Suspected";
  const isNeedsReview = job.investigation_status === "Needs Review";

  const badgeColor = isVerified
    ? "bg-green-500/10 text-green-500 border-green-500/30"
    : isSuspected
    ? "bg-red-500/10 text-red-500 border-red-500/30"
    : "bg-yellow-500/10 text-yellow-500 border-yellow-500/30";

  const StatusIcon = isVerified ? CheckCircle : isSuspected ? ShieldAlert : Clock;

  const score = job.confidence != null ? (job.confidence).toFixed(1) + "%" : "N/A";
  const formattedDate = new Date(job.created_at).toLocaleString();

  return (
    <Link href={job.stage === "completed" ? `/result/${job.job_id}` : `/processing/${job.job_id}`}>
      <Card className="flex flex-col gap-4 hover:border-accent transition-colors cursor-pointer group">
        <div className="flex items-start justify-between">
          <div className="flex flex-col gap-1">
            <span className="font-mono text-xs text-text-secondary">ID: {job.job_id.substring(0, 8)}</span>
            <span className="font-semibold text-white truncate max-w-[200px]" title={job.filename}>
              {job.filename}
            </span>
          </div>
          <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full border text-xs font-medium ${badgeColor}`}>
            <StatusIcon className="w-3 h-3" />
            <span>{job.investigation_status || "Needs Review"}</span>
          </div>
        </div>

        <div className="flex flex-col gap-3 mt-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-text-secondary">Upload Date</span>
            <span className="text-white">{formattedDate}</span>
          </div>
          
          <div className="flex justify-between items-center text-sm">
            <span className="text-text-secondary">Trust Score</span>
            <span className={`font-mono font-medium ${job.verdict === "likely_ai_generated" ? "text-synthetic" : job.verdict === "likely_authentic" ? "text-authentic" : "text-white"}`}>
              {score}
            </span>
          </div>
          
          <div className="flex justify-between items-center text-sm">
            <span className="text-text-secondary">Progress</span>
            <div className="flex items-center gap-2">
              <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent transition-all duration-500" 
                  style={{ width: `${job.stage_progress * 100}%` }}
                />
              </div>
              <span className="font-mono text-xs text-white">{Math.round(job.stage_progress * 100)}%</span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between text-accent group-hover:text-accent-alt transition-colors">
          <span className="text-sm font-medium">View Analysis</span>
          <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}
