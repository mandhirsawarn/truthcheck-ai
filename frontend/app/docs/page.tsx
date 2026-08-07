import React from 'react';
import { Database, Server, Cpu, FileVideo, Activity, Box, ArrowRight, Layers, Layout, Eye, GitCommit } from 'lucide-react';
const ArchitectureDiagram = () => (
  <div className="bg-bg-secondary p-8 rounded-2xl border border-border-subtle my-8 overflow-x-auto shadow-sm">
    <div className="min-w-[800px]">
      <div className="flex items-center justify-between gap-4 mb-12">
        <div className="flex flex-col items-center gap-2">
          <div className="w-20 h-20 rounded-xl bg-accent/10 border border-accent flex items-center justify-center text-accent shadow-inner">
            <FileVideo className="w-8 h-8" />
          </div>
          <span className="text-sm font-medium text-text-secondary">Client Upload</span>
        </div>
        <ArrowRight className="text-text-muted" />
        <div className="flex flex-col items-center gap-2">
          <div className="w-20 h-20 rounded-xl bg-blue-500/10 border border-blue-500 flex items-center justify-center text-blue-500 shadow-inner">
            <Server className="w-8 h-8" />
          </div>
          <span className="text-sm font-medium text-text-secondary">FastAPI Gateway</span>
        </div>
        <ArrowRight className="text-text-muted" />
        <div className="flex-1 border border-border-subtle rounded-xl p-8 bg-bg-primary relative shadow-md">
          <div className="absolute -top-3 left-6 bg-bg-primary px-3 text-xs font-semibold text-accent uppercase tracking-wider border border-border-subtle rounded-full">
            Analysis Pipeline
          </div>
          <div className="flex items-center justify-between gap-4">
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded-lg bg-orange-500/10 border border-orange-500/30 flex items-center justify-center text-orange-500">
                <Layers className="w-6 h-6" />
              </div>
              <span className="text-xs font-medium text-text-muted">Frame Extract</span>
            </div>
            <ArrowRight className="text-text-muted w-4 h-4" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded-lg bg-green-500/10 border border-green-500/30 flex items-center justify-center text-green-500">
                <Eye className="w-6 h-6" />
              </div>
              <span className="text-xs font-medium text-text-muted">Face Detect</span>
            </div>
            <ArrowRight className="text-text-muted w-4 h-4" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-500">
                <Cpu className="w-6 h-6" />
              </div>
              <span className="text-xs font-medium text-text-muted">CNN Inference</span>
            </div>
            <ArrowRight className="text-text-muted w-4 h-4" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded-lg bg-pink-500/10 border border-pink-500/30 flex items-center justify-center text-pink-500">
                <Activity className="w-6 h-6" />
              </div>
              <span className="text-xs font-medium text-text-muted">Aggregation</span>
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center gap-32">
        <div className="flex flex-col items-center gap-2 relative">
          <div className="absolute -top-12 left-1/2 w-0.5 h-10 bg-border-subtle"></div>
          <div className="w-20 h-20 rounded-xl bg-teal-500/10 border border-teal-500 flex items-center justify-center text-teal-500 shadow-inner">
            <Database className="w-8 h-8" />
          </div>
          <span className="text-sm font-medium text-text-secondary">SQLite (Aiosqlite)</span>
        </div>
        <div className="flex flex-col items-center gap-2 relative">
          <div className="absolute -top-12 left-1/2 w-0.5 h-10 bg-border-subtle"></div>
          <div className="w-20 h-20 rounded-xl bg-yellow-500/10 border border-yellow-500 flex items-center justify-center text-yellow-500 shadow-inner">
            <Box className="w-8 h-8" />
          </div>
          <span className="text-sm font-medium text-text-secondary">Local File Storage</span>
        </div>
      </div>
    </div>
  </div>
);
export default function DocsPage() {
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      <div className="container mx-auto px-6 py-16 flex gap-16">
        {}
        <aside className="w-64 shrink-0 hidden lg:block">
          <div className="sticky top-28 bg-bg-secondary p-6 rounded-2xl border border-border-subtle">
            <h3 className="font-bold mb-6 text-white uppercase tracking-wider text-xs">Table of Contents</h3>
            <ul className="space-y-4">
              <li><a href="#overview" className="text-sm font-medium text-text-secondary hover:text-accent transition-colors flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-border-subtle"></div> System Overview</a></li>
              <li><a href="#architecture" className="text-sm font-medium text-text-secondary hover:text-accent transition-colors flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-border-subtle"></div> Architecture</a></li>
              <li><a href="#pipeline" className="text-sm font-medium text-text-secondary hover:text-accent transition-colors flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-border-subtle"></div> Full Pipeline (A-Z)</a></li>
              <li><a href="#api" className="text-sm font-medium text-text-secondary hover:text-accent transition-colors flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-border-subtle"></div> API Routes</a></li>
              <li><a href="#ml" className="text-sm font-medium text-text-secondary hover:text-accent transition-colors flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-border-subtle"></div> ML Specs</a></li>
            </ul>
          </div>
        </aside>
        {}
        <main className="flex-1 max-w-4xl pb-24">
          <div className="mb-20">
            <h1 className="text-5xl font-bold tracking-tight mb-6 text-white">System Documentation</h1>
            <p className="text-xl text-text-secondary leading-relaxed">
              A comprehensive A-Z guide of the Truth Check System. Understand the underlying architecture, data flow, API integration, and machine learning pipelines.
            </p>
          </div>
          <section id="overview" className="mb-20 scroll-mt-32">
            <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3 text-white">
              <Layout className="w-8 h-8 text-accent" />
              1. System Overview
            </h2>
            <p className="text-text-secondary leading-relaxed mb-4 text-lg">
              Truth Check is an enterprise-grade deepfake and synthetic media detection system. Built on a modern tech stack featuring <strong className="text-white">Next.js (React)</strong> on the frontend and <strong className="text-white">FastAPI (Python)</strong> on the backend, it provides real-time, asynchronous video analysis with seamless UX.
            </p>
            <p className="text-text-secondary leading-relaxed text-lg">
              At its core, the system processes uploaded media, extracts frames, detects facial landmarks, and runs them through a state-of-the-art <strong className="text-white">Convolutional Neural Network (EfficientNet_b0)</strong> to determine authenticity.
            </p>
          </section>
          <section id="architecture" className="mb-20 scroll-mt-32">
            <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3 text-white">
              <GitCommit className="w-8 h-8 text-accent" />
              2. Architecture Diagram
            </h2>
            <p className="text-text-secondary leading-relaxed mb-8 text-lg">
              The system operates completely asynchronously to ensure a highly responsive user experience. Heavy video processing is handed off to background worker tasks, while WebSockets stream live status updates directly to the browser.
            </p>
            <ArchitectureDiagram />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div className="p-8 bg-bg-secondary rounded-2xl border border-border-subtle hover:border-accent/50 transition-colors">
                <h3 className="font-bold text-xl mb-3 text-white">Frontend (Next.js)</h3>
                <p className="text-text-secondary leading-relaxed">Handles file uploads, displays real-time progress bars via WebSockets, and renders beautiful analytics dashboards for the final verdict.</p>
              </div>
              <div className="p-8 bg-bg-secondary rounded-2xl border border-border-subtle hover:border-accent/50 transition-colors">
                <h3 className="font-bold text-xl mb-3 text-white">Backend (FastAPI)</h3>
                <p className="text-text-secondary leading-relaxed">Serves as the central API gateway. Manages the SQLite database via <code>aiosqlite</code>, routes API traffic, and orchestrates background ML workers.</p>
              </div>
            </div>
          </section>
          <section id="pipeline" className="mb-20 scroll-mt-32">
            <h2 className="text-3xl font-semibold mb-10 flex items-center gap-3 text-white">
              <Layers className="w-8 h-8 text-accent" />
              3. Analysis Pipeline (A-Z)
            </h2>
            <div className="space-y-12 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-1 before:bg-gradient-to-b before:from-accent/50 before:via-border-subtle before:to-transparent">
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-bg-primary bg-orange-500 text-bg-primary shadow-xl shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 font-bold text-lg z-10">1</div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] bg-bg-secondary p-8 rounded-2xl border border-border-subtle shadow-lg">
                  <h4 className="font-bold text-xl text-white mb-3">Ingestion & Extraction</h4>
                  <p className="text-text-secondary leading-relaxed">The video is uploaded and stored securely. <code>extract_frames.py</code> uses OpenCV to slice the video into discrete images at a specific FPS to balance accuracy and processing speed.</p>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-bg-primary bg-green-500 text-bg-primary shadow-xl shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 font-bold text-lg z-10">2</div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] bg-bg-secondary p-8 rounded-2xl border border-border-subtle shadow-lg">
                  <h4 className="font-bold text-xl text-white mb-3">Face Detection</h4>
                  <p className="text-text-secondary leading-relaxed"><code>face_detect.py</code> scans each extracted frame to isolate human faces. Background noise is cropped out, and the faces are aligned and resized to exactly 224x224 pixels.</p>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-bg-primary bg-purple-500 text-bg-primary shadow-xl shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 font-bold text-lg z-10">3</div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] bg-bg-secondary p-8 rounded-2xl border border-border-subtle shadow-lg">
                  <h4 className="font-bold text-xl text-white mb-3">Deep Inference</h4>
                  <p className="text-text-secondary leading-relaxed">The cropped faces are passed to <code>inference.py</code>. Our customized Convolutional Neural Network (CNN) evaluates the facial artifacts, analyzing lighting, edges, and blending inconsistencies frame-by-frame.</p>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-bg-primary bg-pink-500 text-bg-primary shadow-xl shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 font-bold text-lg z-10">4</div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] bg-bg-secondary p-8 rounded-2xl border border-border-subtle shadow-lg">
                  <h4 className="font-bold text-xl text-white mb-3">Verdict Aggregation</h4>
                  <p className="text-text-secondary leading-relaxed">Finally, <code>aggregate.py</code> statistically combines the frame-level confidence scores to produce a definitive <strong>Real</strong> or <strong>Fake</strong> verdict for the entire video, smoothing out statistical outliers.</p>
                </div>
              </div>
            </div>
          </section>
          <section id="api" className="mb-20 scroll-mt-32">
            <h2 className="text-3xl font-semibold mb-8 flex items-center gap-3 text-white">
              <Server className="w-8 h-8 text-accent" />
              4. API Routes
            </h2>
            <div className="space-y-6">
              <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-8 hover:border-green-500/50 transition-colors">
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-4 py-1.5 rounded-lg bg-green-500/20 text-green-400 text-sm font-bold font-mono tracking-widest">POST</span>
                  <code className="text-xl font-mono text-white">/api/analyze</code>
                </div>
                <p className="text-text-secondary text-lg leading-relaxed">Accepts a <code>multipart/form-data</code> upload containing the target video. Initiates the background processing pipeline and immediately returns a unique <code>job_id</code> for tracking.</p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-8 hover:border-blue-500/50 transition-colors">
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-4 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 text-sm font-bold font-mono tracking-widest">GET</span>
                  <code className="text-xl font-mono text-white">/api/status/{"{job_id}"}</code>
                </div>
                <p className="text-text-secondary text-lg leading-relaxed">REST Polling endpoint. Returns the current state of the job (<code>processing</code>, <code>completed</code>, <code>failed</code>), along with percentage completion and detailed stage metadata.</p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-8 hover:border-blue-500/50 transition-colors">
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-4 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 text-sm font-bold font-mono tracking-widest">GET</span>
                  <code className="text-xl font-mono text-white">/api/results/{"{job_id}"}</code>
                </div>
                <p className="text-text-secondary text-lg leading-relaxed">Fetches the comprehensive analysis result, including the final verdict, confidence score, frame-by-frame timeline data, and execution metrics.</p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-8 hover:border-yellow-500/50 transition-colors">
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-4 py-1.5 rounded-lg bg-yellow-500/20 text-yellow-400 text-sm font-bold font-mono tracking-widest">WS</span>
                  <code className="text-xl font-mono text-white">/api/ws/{"{job_id}"}</code>
                </div>
                <p className="text-text-secondary text-lg leading-relaxed">A persistent WebSocket connection. The backend streams live JSON payloads outlining exact processing steps (e.g., "Extracting frame 45/150") for highly reactive, sub-second UI updates.</p>
              </div>
            </div>
          </section>
          <section id="ml" className="mb-20 scroll-mt-32">
            <h2 className="text-3xl font-semibold mb-8 flex items-center gap-3 text-white">
              <Cpu className="w-8 h-8 text-accent" />
              5. Machine Learning Specs
            </h2>
            <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-10">
              <p className="text-text-secondary leading-relaxed text-lg mb-8">
                The core intelligence is powered by <strong className="text-white">EfficientNet_b0</strong>, fine-tuned specifically on synthetic artifact datasets for maximum deepfake identification capability.
              </p>
              <div className="grid gap-6">
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded bg-accent/20 text-accent flex items-center justify-center shrink-0 mt-1">✓</div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Architecture</h4>
                    <p className="text-text-secondary">EfficientNet_b0 (Pre-trained on ImageNet, fine-tuned for Deepfake detection)</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded bg-accent/20 text-accent flex items-center justify-center shrink-0 mt-1">✓</div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Input Shape</h4>
                    <p className="text-text-secondary">224 x 224 RGB tensors, normalized with mean <code>[0.485, 0.456, 0.406]</code> and std <code>[0.229, 0.224, 0.225]</code></p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded bg-accent/20 text-accent flex items-center justify-center shrink-0 mt-1">✓</div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Optimization</h4>
                    <p className="text-text-secondary">AdamW optimizer, Cosine Annealing Learning Rate scheduler</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded bg-accent/20 text-accent flex items-center justify-center shrink-0 mt-1">✓</div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Framework</h4>
                    <p className="text-text-secondary">PyTorch 2.1+, leveraging <code>timm</code> for model architecture, and Apple Metal Performance Shaders (MPS) or CUDA for hardware acceleration</p>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
