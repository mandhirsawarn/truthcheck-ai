"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, UserCircle } from "lucide-react";
import { useRole, Role } from "@/context/RoleContext";

export function Header() {
  const { role, setRole } = useRole();
  return (
    <motion.header 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="h-[72px] flex items-center glass-panel sticky top-0 z-50 shadow-sm shadow-accent/5"
    >
      <div className="container mx-auto px-6 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <motion.div 
            whileHover={{ rotate: 180, scale: 1.1 }}
            transition={{ duration: 0.4 }}
            className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center border border-accent/50 shadow-[0_0_10px_rgba(108,99,255,0.3)]"
          >
            <Sparkles className="w-4 h-4 text-accent-alt" />
          </motion.div>
          <div className="flex flex-col">
            <span className="font-bold tracking-tight text-lg text-white leading-none">Truth Check</span>
            <span className="text-[10px] text-text-secondary uppercase tracking-wider mt-1 font-medium">Think Before You Trust</span>
          </div>
        </Link>
        <nav className="flex items-center gap-8 text-sm font-medium">
          <Link href="/dashboard" className="text-text-secondary hover:text-white transition-colors relative group">
            Dashboard
            <span className="absolute -bottom-1 left-0 w-0 h-[2px] bg-accent transition-all duration-300 group-hover:w-full rounded-full"></span>
          </Link>
          <Link href="/docs" className="text-text-secondary hover:text-white transition-colors relative group">
            Docs
            <span className="absolute -bottom-1 left-0 w-0 h-[2px] bg-accent transition-all duration-300 group-hover:w-full rounded-full"></span>
          </Link>
          <Link
            href="/upload"
            className="text-white hover:glow-text transition-all duration-300 bg-white/5 px-4 py-2 rounded-full border border-white/10 hover:border-accent/50 hover:bg-accent/10"
          >
            Try Detector
          </Link>
          
          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-white/10">
            <UserCircle className="w-4 h-4 text-accent" />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
              className="bg-transparent text-text-primary text-sm font-medium focus:outline-none focus:ring-0 cursor-pointer hover:text-white transition-colors [&>option]:bg-bg-surface"
            >
              <option value="Admin">Admin</option>
              <option value="Investigator">Investigator</option>
              <option value="Reviewer">Reviewer</option>
            </select>
          </div>
        </nav>
      </div>
    </motion.header>
  );
}
