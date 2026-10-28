"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CheckSquare, MessageSquare, Code2 } from "lucide-react";

export default function SkillsArenaNav() {
  const pathname = usePathname() || "";
  const isAptitude = pathname.includes("/aptitude");
  const isGD = pathname.includes("/gd-room");
  const isCode = pathname.includes("/code-arena");

  return (
    <div className="mb-6 rounded-xl border border-slate-200 bg-white p-2.5 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 pl-2 text-xs font-bold uppercase tracking-wider text-slate-500">
          <span>Placement Modules</span>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <Link
            href="/skillsarena/aptitude"
            className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition ${
              isAptitude
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900"
            }`}
          >
            <CheckSquare className="h-3.5 w-3.5" />
            <span>Aptitude Assessment</span>
          </Link>

          <Link
            href="/skillsarena/gd-room"
            className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition ${
              isGD
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900"
            }`}
          >
            <MessageSquare className="h-3.5 w-3.5" />
            <span>GD Arena</span>
          </Link>

          <Link
            href="/skillsarena/code-arena"
            className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition ${
              isCode
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900"
            }`}
          >
            <Code2 className="h-3.5 w-3.5" />
            <span>Code Arena</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
