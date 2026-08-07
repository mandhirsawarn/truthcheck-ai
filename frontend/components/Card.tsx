"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import { motion, HTMLMotionProps } from "framer-motion";
export const Card = React.forwardRef<HTMLDivElement, Omit<HTMLMotionProps<"div">, "ref">>(
  ({ className, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={cn(
        "glass-card p-6 relative overflow-hidden group transition-all duration-300 hover:shadow-[0_8px_30px_rgba(108,99,255,0.1)] hover:border-accent/30",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      {props.children as React.ReactNode}
    </motion.div>
  )
);
Card.displayName = "Card";
