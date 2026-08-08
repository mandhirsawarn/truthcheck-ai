"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle } from "lucide-react";

export type ToastType = "success" | "error";

interface ToastProps {
  message: string;
  type: ToastType;
  isVisible: boolean;
  onClose: () => void;
}

export function Toast({ message, type, isVisible, onClose }: ToastProps) {
  const Icon = type === "success" ? CheckCircle2 : XCircle;
  const bgColor = type === "success" ? "bg-authentic/10 border-authentic/30" : "bg-synthetic/10 border-synthetic/30";
  const iconColor = type === "success" ? "text-authentic" : "text-synthetic";

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 100 }}
          className={`fixed top-24 right-6 z-50 flex items-start gap-3 p-4 rounded-lg border shadow-xl backdrop-blur-md max-w-sm ${bgColor}`}
        >
          <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${iconColor}`} />
          <div className="flex flex-col gap-1">
            <h4 className={`text-sm font-semibold ${type === "success" ? "text-authentic" : "text-synthetic"}`}>
              {type === "success" ? "Investigation Saved Successfully" : "Failed to Save Investigation"}
            </h4>
            <p className="text-sm text-text-secondary">{message}</p>
          </div>
          <button onClick={onClose} className="ml-auto text-text-secondary hover:text-white shrink-0">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
