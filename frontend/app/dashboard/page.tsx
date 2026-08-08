"use client";

import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { useJobs } from "@/lib/hooks";
import { EvidenceCard } from "@/components/EvidenceCard";
import { ShieldCheck, AlertTriangle, Clock, Activity } from "lucide-react";

export default function DashboardPage() {
  const [filter, setFilter] = useState<"All" | "Verified" | "Suspected" | "Needs Review">("All");
  
  // For a real app with many jobs, we'd use pagination, but here we'll fetch a large page for simplicity
  const { data: jobsData, isLoading, isError } = useJobs(1, 100);

  const stats = useMemo(() => {
    if (!jobsData?.jobs) return { total: 0, verified: 0, suspected: 0, needsReview: 0 };
    return {
      total: jobsData.jobs.length,
      verified: jobsData.jobs.filter(j => j.investigation_status === "Verified").length,
      suspected: jobsData.jobs.filter(j => j.investigation_status === "Suspected").length,
      needsReview: jobsData.jobs.filter(j => j.investigation_status === "Needs Review" || !j.investigation_status).length,
    };
  }, [jobsData]);

  const filteredJobs = useMemo(() => {
    if (!jobsData?.jobs) return [];
    if (filter === "All") return jobsData.jobs;
    return jobsData.jobs.filter(j => j.investigation_status === filter || (!j.investigation_status && filter === "Needs Review"));
  }, [jobsData, filter]);

  if (isLoading) {
    return (
      <div className="flex-grow flex items-center justify-center">
        <Activity className="w-8 h-8 text-accent animate-pulse" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex-grow flex items-center justify-center text-synthetic font-mono">
        Error loading dashboard data.
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-12 flex-grow">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Investigation Dashboard</h1>
          <p className="text-text-secondary mt-1 text-sm">Monitor and manage analyzed evidence</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard title="Total Evidence" value={stats.total} icon={<Activity className="text-blue-500 w-5 h-5" />} />
          <StatCard title="Verified" value={stats.verified} icon={<ShieldCheck className="text-green-500 w-5 h-5" />} />
          <StatCard title="Suspected" value={stats.suspected} icon={<AlertTriangle className="text-red-500 w-5 h-5" />} />
          <StatCard title="Needs Review" value={stats.needsReview} icon={<Clock className="text-yellow-500 w-5 h-5" />} />
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 border-b border-white/10 pb-4 mt-8">
          {["All", "Verified", "Suspected", "Needs Review"].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab as any)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === tab 
                  ? "bg-accent/20 text-accent border border-accent/50" 
                  : "bg-transparent text-text-secondary hover:text-white hover:bg-white/5"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Evidence Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredJobs.length === 0 ? (
            <div className="col-span-full py-12 text-center text-text-secondary font-mono text-sm">
              No evidence found for the selected filter.
            </div>
          ) : (
            filteredJobs.map((job) => (
              <motion.div
                key={job.job_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <EvidenceCard job={job} />
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string; value: number; icon: React.ReactNode }) {
  return (
    <div className="glass-card p-6 flex flex-col gap-2 rounded-xl border-border-subtle bg-bg-surface/50">
      <div className="flex justify-between items-start">
        <span className="text-text-secondary text-sm font-medium">{title}</span>
        {icon}
      </div>
      <span className="text-3xl font-bold text-white font-mono">{value}</span>
    </div>
  );
}
