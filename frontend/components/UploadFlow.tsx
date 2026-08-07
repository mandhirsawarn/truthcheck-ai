"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, FileVideo, Scan, Activity, FileCheck, BrainCircuit } from "lucide-react";
import { Card } from "./Card";
import { Button } from "./Button";
import { api } from "@/lib/api";
import { formatBytes, formatDuration } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";

const CHUNK_SIZE = 5 * 1024 * 1024;

export function UploadFlow() {
  const [file, setFile] = useState<File | null>(null);
  const [thumbnail, setThumbnail] = useState<string | null>(null);
  const [duration, setDuration] = useState<number>(0);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSpeed, setUploadSpeed] = useState(0);
  const [uploadState, setUploadState] = useState<
    "idle" | "selected" | "uploading" | "validating" | "queued" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateThumbnail = (file: File) => {
    const video = document.createElement("video");
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    video.autoplay = false;
    video.muted = true;
    const url = URL.createObjectURL(file);
    video.src = url;
    video.onloadeddata = () => {
      setDuration(video.duration);
      video.currentTime = Math.min(1.0, video.duration / 2);
    };
    video.onseeked = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
      setThumbnail(canvas.toDataURL("image/jpeg"));
      URL.revokeObjectURL(url);
    };
  };

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.type.startsWith("video/")) {
      setErrorMessage("Please select a valid video file.");
      return;
    }
    if (selectedFile.size > 2 * 1024 * 1024 * 1024) {
      setErrorMessage("File exceeds 2GB limit.");
      return;
    }
    setFile(selectedFile);
    setUploadState("selected");
    setErrorMessage("");
    generateThumbnail(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("No file selected");
      setUploadState("uploading");
      const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
      const initRes = await api.initUpload({
        filename: file.name,
        file_size_bytes: file.size,
        mime_type: file.type,
        total_chunks: totalChunks,
      });
      const startTime = Date.now();
      let uploadedBytes = 0;
      for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);
        await api.uploadChunk(initRes.job_id, i, chunk);
        uploadedBytes += chunk.size;
        const progress = (uploadedBytes / file.size) * 100;
        setUploadProgress(progress);
        const elapsed = (Date.now() - startTime) / 1000;
        setUploadSpeed(uploadedBytes / elapsed);
      }
      setUploadState("validating");
      await api.completeUpload(initRes.job_id, totalChunks);
      setUploadState("queued");
      return initRes.job_id;
    },
    onSuccess: (jobId) => {
      router.push(`/processing/${jobId}`);
    },
    onError: (err: any) => {
      setUploadState("error");
      setErrorMessage(err?.response?.data?.message || err.message || "Upload failed");
    },
  });

  const remainingSeconds = uploadSpeed > 0 && file ? (file.size * (1 - uploadProgress / 100)) / uploadSpeed : 0;

  if (uploadState === "idle" || uploadState === "error") {
    return (
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-4xl mx-auto pt-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">Start Forensic Analysis</h2>
          <p className="text-text-secondary">Upload a video to instantly detect AI manipulation and generative artifacts.</p>
        </div>

        <motion.div
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className={`relative group rounded-3xl p-[1px] transition-all duration-300 ${
            isDragging ? "bg-accent shadow-[0_0_50px_rgba(108,99,255,0.3)]" : "bg-border-subtle hover:bg-white/20 hover:shadow-[0_0_30px_rgba(255,255,255,0.1)]"
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {/* Animated glowing border effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-accent via-accent-alt to-accent opacity-0 group-hover:opacity-100 rounded-3xl blur-xl transition-opacity duration-500 -z-10" />
          
          <div className="glass-card cursor-pointer rounded-[23px] p-24 flex flex-col items-center justify-center text-center h-[400px]">
            <input
              type="file"
              className="hidden"
              accept="video/*"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            />
            
            <motion.div 
              animate={isDragging ? { y: -10, scale: 1.1 } : { y: 0, scale: 1 }}
              className="w-20 h-20 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:border-accent/50 group-hover:bg-accent/10 transition-colors"
            >
              <Upload className="w-8 h-8 text-white group-hover:text-accent-alt transition-colors" />
            </motion.div>
            
            <h3 className="text-2xl font-bold text-white mb-2">Drag & Drop Video</h3>
            <p className="text-text-secondary mb-8">or click to browse from your device</p>
            
            <div className="flex gap-4 items-center px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs text-text-secondary font-mono">
              <span className="flex items-center gap-1"><FileCheck className="w-3 h-3 text-authentic" /> MP4, MOV, WEBM</span>
              <span className="w-1 h-1 rounded-full bg-border-subtle" />
              <span>Up to 2GB</span>
            </div>
          </div>
        </motion.div>

        {errorMessage && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8 p-4 rounded-xl border border-synthetic/30 bg-synthetic/10 text-synthetic text-sm font-medium text-center glass-card">
            {errorMessage}
          </motion.div>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-3xl mx-auto pt-16">
      <Card className="flex flex-col gap-8 p-8 border-accent/20 shadow-[0_20px_50px_rgba(108,99,255,0.1)]">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-6">
            {thumbnail ? (
              <div className="relative rounded-lg overflow-hidden border border-white/10 shadow-lg">
                <img src={thumbnail} alt="Thumbnail" className="w-32 h-auto aspect-video object-cover" />
                {uploadState !== "selected" && (
                  <motion.div 
                    animate={{ y: ["-10%", "110%"] }} 
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 h-1/2 bg-gradient-to-b from-transparent to-accent/50 pointer-events-none" 
                  />
                )}
              </div>
            ) : (
              <div className="w-32 aspect-video bg-white/5 rounded-lg border border-white/10 flex items-center justify-center text-text-secondary">
                <FileVideo className="w-8 h-8" />
              </div>
            )}
            
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-lg text-white">{file?.name}</span>
              <div className="flex items-center gap-3 text-sm font-mono text-text-secondary">
                <span className="bg-white/5 px-2 py-1 rounded border border-white/10">{formatBytes(file?.size || 0)}</span>
                {duration > 0 && <span className="bg-white/5 px-2 py-1 rounded border border-white/10">{formatDuration(duration)}</span>}
                <span className="uppercase text-accent-alt">{file?.type.split('/')[1] || "unknown"}</span>
              </div>
            </div>
          </div>
          
          {uploadState === "selected" && (
            <button onClick={() => { setFile(null); setUploadState("idle"); }} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-text-secondary hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {uploadState === "selected" ? (
          <div className="flex justify-end pt-4 border-t border-border-subtle">
            <Button size="lg" onClick={() => uploadMutation.mutate()} disabled={uploadMutation.isPending} className="w-full md:w-auto">
              Initialize AI Scan
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-6 pt-6 border-t border-border-subtle">
            
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-end">
                <div className="flex items-center gap-3">
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: "linear" }}>
                    <Scan className="w-5 h-5 text-accent" />
                  </motion.div>
                  <span className="text-white font-medium text-lg">
                    {uploadState === "uploading" && "Securely Uploading Data..."}
                    {uploadState === "validating" && "Verifying Codec Integrity..."}
                    {uploadState === "queued" && "Waking AI Models..."}
                  </span>
                </div>
                <span className="font-mono text-xl text-accent-alt font-bold">
                  {uploadState === "uploading" ? `${uploadProgress.toFixed(0)}%` : ""}
                </span>
              </div>
              
              <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden border border-white/10 relative">
                <motion.div 
                  initial={{ width: "0%" }}
                  animate={{ width: `${uploadState === "uploading" ? uploadProgress : 100}%` }}
                  transition={{ ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-accent to-accent-alt relative"
                >
                  <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:16px_16px] animate-[slide_1s_linear_infinite]" />
                </motion.div>
              </div>

              {uploadState === "uploading" && (
                <div className="flex justify-between items-center text-sm font-mono text-text-secondary mt-1">
                  <span>{formatBytes(uploadSpeed)}/s</span>
                  <span className="flex items-center gap-2">
                    <Activity className="w-3 h-3 text-accent" />
                    {remainingSeconds > 0 ? formatDuration(remainingSeconds) : "00:00"} remaining
                  </span>
                </div>
              )}
            </div>
            
            {/* Fake AI Scanning Log UI */}
            <div className="bg-[#03040B] rounded-xl p-4 font-mono text-xs text-text-secondary h-32 overflow-hidden border border-white/5 relative shadow-inner">
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_14px]" />
              <div className="relative z-10 flex flex-col gap-2 opacity-80">
                <p className="text-accent">{'>'} Initiating secure connection...</p>
                {uploadProgress > 0 && <p className="text-white">{'>'} Transferring chunked payload [{Math.floor(uploadProgress)}%]</p>}
                {uploadProgress > 50 && <p className="text-white">{'>'} Allocating tensor memory...</p>}
                {uploadState === "validating" && <p className="text-accent-alt">{'>'} Performing format verification...</p>}
                {uploadState === "queued" && <p className="text-authentic">{'>'} Payload received. Models ready.</p>}
                <motion.div animate={{ opacity: [1, 0, 1] }} transition={{ duration: 0.8, repeat: Infinity }}>_</motion.div>
              </div>
            </div>

          </div>
        )}
      </Card>
    </motion.div>
  );
}
