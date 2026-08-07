"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { ShieldCheck, Activity, Layers, Scan, Cpu } from "lucide-react";

export default function LandingPage() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.2 },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.8 } },
  };

  return (
    <div className="flex-grow flex flex-col relative overflow-hidden">
      {/* Abstract Background Blobs */}
      <motion.div 
        animate={{ rotate: 360, scale: [1, 1.2, 1] }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute -top-32 -left-32 w-96 h-96 bg-accent/20 rounded-full blur-[120px] pointer-events-none" 
      />
      <motion.div 
        animate={{ rotate: -360, scale: [1, 1.5, 1] }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/2 -right-32 w-[30rem] h-[30rem] bg-accent-alt/10 rounded-full blur-[120px] pointer-events-none" 
      />

      <section className="container mx-auto px-6 pt-32 pb-40 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
        <motion.div variants={container} initial="hidden" animate="show" className="flex flex-col items-start gap-8">
          <motion.div variants={item} className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-accent/30 bg-accent/10 text-accent text-sm font-medium">
            <ShieldCheck className="w-4 h-4" />
            <span>Forensic AI Platform v2.0</span>
          </motion.div>
          <motion.h1 variants={item} className="text-6xl md:text-7xl leading-[1.1] font-bold text-white tracking-tight">
            Detect AI <br /> Manipulated <br />
            <span className="animated-gradient-text glow-text">Videos Instantly.</span>
          </motion.h1>
          <motion.p variants={item} className="text-xl text-text-secondary max-w-lg font-light leading-relaxed">
            The most advanced forensic analysis platform for detecting AI-generated and manipulated video content with frame-level precision. Built for enterprise truth verification.
          </motion.p>
          <motion.div variants={item} className="flex items-center gap-6 pt-6">
            <Link href="/upload">
              <Button size="lg" className="px-10 py-4 text-base font-semibold">
                Start Analysis
              </Button>
            </Link>
            <Link href="/docs" className="text-text-secondary hover:text-white transition-colors flex items-center gap-2 group">
              See How It Works
              <span className="transform transition-transform group-hover:translate-x-1">→</span>
            </Link>
          </motion.div>
        </motion.div>

        {/* Hero Visual */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, rotateX: 10 }}
          animate={{ opacity: 1, scale: 1, rotateX: 0 }}
          transition={{ duration: 1.2, ease: "easeOut", delay: 0.4 }}
          className="relative perspective-1000"
        >
          <div className="glass-card p-2 rounded-2xl shadow-[0_20px_50px_rgba(108,99,255,0.15)] border-accent/20 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-tr from-accent/10 to-accent-alt/10 opacity-50" />
            <div className="aspect-[4/3] bg-bg-primary rounded-xl overflow-hidden relative border border-white/5 flex flex-col">
              
              {/* Fake UI Header */}
              <div className="h-10 border-b border-border-subtle flex items-center px-4 justify-between bg-white/5">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <div className="px-3 py-1 bg-white/5 rounded text-xs font-mono text-text-secondary">deepfake_scan.mp4</div>
              </div>

              {/* Fake UI Body */}
              <div className="flex-grow flex items-center justify-center relative p-8 gap-8">
                {/* Scanning Animation overlay */}
                <motion.div 
                  animate={{ y: ["-100%", "100%"] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 h-1/3 bg-gradient-to-b from-transparent via-accent/20 to-accent shadow-[0_2px_20px_rgba(108,99,255,0.8)] z-20 pointer-events-none"
                />

                <div className="flex-1 h-full border border-border-subtle rounded-lg bg-bg-surface flex items-center justify-center relative overflow-hidden">
                   <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
                   <Scan className="w-24 h-24 text-accent/50 animate-pulse" />
                </div>

                <div className="w-48 flex flex-col gap-4 z-10">
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1 }}
                    className="glass-card p-4 flex flex-col gap-1 border-authentic/30 bg-authentic/5"
                  >
                    <span className="font-mono text-authentic text-xl font-bold tracking-wider">98.3%</span>
                    <span className="text-xs text-text-secondary uppercase">Authentic</span>
                  </motion.div>
                  <div className="h-px w-full bg-gradient-to-r from-transparent via-border-subtle to-transparent" />
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.2 }}
                    className="glass-card p-4 flex flex-col gap-1 border-synthetic/30 bg-synthetic/5"
                  >
                    <span className="font-mono text-synthetic text-xl font-bold tracking-wider">High</span>
                    <span className="text-xs text-text-secondary uppercase">Risk Level</span>
                  </motion.div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative py-32 bg-black/40 border-t border-border-subtle">
        <div className="container mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Unrivaled Forensic Accuracy</h2>
            <p className="text-text-secondary text-lg max-w-2xl mx-auto">Our multi-modal engine analyzes video across multiple dimensions simultaneously.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: <Layers className="w-6 h-6 text-accent" />,
                title: "Spatial Artifacts",
                desc: "CNNs detect pixel-level blending artifacts, unnatural textures, and generative anomalies frame by frame."
              },
              {
                icon: <Activity className="w-6 h-6 text-accent-alt" />,
                title: "Temporal Consistency",
                desc: "Analyzes inter-frame motion vectors to identify synthetic flicker and unnatural stillness."
              },
              {
                icon: <Cpu className="w-6 h-6 text-[#4ADE80]" />,
                title: "Frequency Domain",
                desc: "FFT identifies characteristic spectral peaks unique to GAN and diffusion-based generation."
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2, duration: 0.6 }}
              >
                <Card className="h-full hover:bg-white/5 cursor-default">
                  <div className="w-12 h-12 rounded-full glass-card flex items-center justify-center mb-6">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                  <p className="text-text-secondary leading-relaxed">{feature.desc}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
