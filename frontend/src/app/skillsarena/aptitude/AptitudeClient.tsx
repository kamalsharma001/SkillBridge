"use client";

import Navbar from "../../components/Navbar";
import SkillsArenaNav from "../../components/SkillsArenaNav";
import AptitudeArena from "../../components/AptitudeArena";
import { getApiBase } from "../../utils/apiBase";

export default function AptitudeClient() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      <Navbar />
      <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8">
        <SkillsArenaNav />
      </div>
      <AptitudeArena apiBase={getApiBase()} />
    </main>
  );
}
