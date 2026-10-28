"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Layers, Briefcase, Trophy } from "lucide-react";

export default function Navbar({ candidateName }: { candidateName?: string }) {
  const pathname = usePathname() || "";
  const isCareer = pathname.startsWith("/careerarena");
  const isSkills = pathname.startsWith("/skillsarena");

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 transition hover:opacity-90">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
            <Layers className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">SkillBridge</span>
        </Link>

        {/* The Two Main Sections in Navbar */}
        <nav className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 p-1">
          <Link
            href="/careerarena"
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
              isCareer
                ? "bg-white text-indigo-600 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Briefcase className="h-3.5 w-3.5" />
            <span>CareerArena</span>
          </Link>
          <Link
            href="/skillsarena/aptitude"
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
              isSkills
                ? "bg-white text-indigo-600 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Trophy className="h-3.5 w-3.5" />
            <span>SkillsArena</span>
          </Link>
        </nav>

        {/* Right Status Indicator */}
        <div className="flex items-center gap-3">
          {candidateName ? (
            <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-800 sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="truncate max-w-[140px]">{candidateName}</span>
            </div>
          ) : (
            <div className="hidden items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600 sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Engine: Port 8000</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
