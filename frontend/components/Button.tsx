"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import { motion, HTMLMotionProps } from "framer-motion";
export interface ButtonProps extends Omit<HTMLMotionProps<"button">, "ref"> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline";
  size?: "default" | "sm" | "lg";
}
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "default", ...props }, ref) => {
    const variants = {
      primary: "bg-accent text-white shadow-[0_0_20px_rgba(108,99,255,0.4)] border border-accent/50",
      secondary: "glass-card text-text-primary hover:bg-white/5",
      danger: "bg-synthetic/80 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)] border border-synthetic/50",
      ghost: "bg-transparent text-text-secondary hover:text-white hover:bg-white/5",
      outline: "border border-border-subtle bg-transparent text-text-primary hover:bg-white/5",
    };
    const sizes = {
      default: "px-6 py-2.5 text-sm rounded-full",
      sm: "px-4 py-2 text-xs rounded-full",
      lg: "px-8 py-3.5 text-base rounded-full",
    };
    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-50 disabled:pointer-events-none relative overflow-hidden group",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        <span className="relative z-10">{props.children as React.ReactNode}</span>
        {variant === "primary" && (
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out z-0 rounded-full" />
        )}
      </motion.button>
    );
  }
);
Button.displayName = "Button";
