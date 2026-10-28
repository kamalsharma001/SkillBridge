import Link from "next/link";
import Navbar from "./components/Navbar";
import {
  Briefcase,
  Trophy,
  ArrowRight,
  BrainCircuit,
  MessageSquare,
  Code2,
  CheckCircle2,
  Layers,
  Sparkles,
  Check,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      <Navbar />

      {/* Main Container */}
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {/* SaaS Hero Section */}
        <section className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200/80 bg-indigo-50/70 px-3.5 py-1 text-xs font-semibold text-indigo-700 shadow-xs mb-5">
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI Career & Placement Arena</span>
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-5xl sm:leading-tight">
            Accelerate your career readiness & placement success
          </h1>

          <p className="mt-4 text-base leading-relaxed text-slate-600 sm:text-lg">
            A unified preparation platform combining AI-driven resume calibration and multi-agent career planning with real-time interactive technical arenas.
          </p>
        </section>

        {/* The Two Main Sections: CareerArena & SkillsArena */}
        <section className="grid gap-8 lg:grid-cols-2 mb-16">
          {/* Card 1: CareerArena */}
          <div className="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 sm:p-9 shadow-xs transition hover:border-indigo-300 hover:shadow-md">
            <div>
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 ring-1 ring-indigo-200/60">
                  <Briefcase className="h-6 w-6" />
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  AI Multi-Agent System
                </span>
              </div>

              <h2 className="mt-6 text-2xl font-bold tracking-tight text-slate-950">
                CareerArena
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                AI resume analysis and career calibration. Parse candidate credentials, calibrate readiness against target industry roles, identify skill gaps, and receive agent-curated learning roadmaps.
              </p>

              <div className="mt-6 border-t border-slate-100 pt-6">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Key Capabilities
                </span>
                <ul className="mt-3 space-y-2.5">
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span>Instant PDF/DOCX parsing of skills, projects, and credentials</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span>Role-specific readiness scoring and skill gap identification</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span>Specialized multi-agent feedback pipeline & reasoning logs</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span>Targeted learning plans with matched job opportunities</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100">
              <Link
                href="/careerarena"
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-700 active:scale-[0.99]"
              >
                <span>Launch CareerArena</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Card 2: SkillsArena */}
          <div className="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 sm:p-9 shadow-xs transition hover:border-indigo-300 hover:shadow-md">
            <div>
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-900 text-white shadow-xs">
                  <Trophy className="h-6 w-6" />
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  Interactive Evaluation
                </span>
              </div>

              <h2 className="mt-6 text-2xl font-bold tracking-tight text-slate-950">
                SkillsArena
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                Comprehensive evaluation arena for placement preparation. Practice timed aptitude assessments, participate in structured group discussions, and write code collaboratively.
              </p>

              <div className="mt-6 border-t border-slate-100 pt-6">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Interactive Modules
                </span>
                <ul className="mt-3 space-y-2.5">
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span><strong>Aptitude Assessment:</strong> Timed questions with step-by-step logic</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span><strong>GD Arena:</strong> Multi-user rooms with speaking turns & mic audio</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span><strong>Code Arena:</strong> Real-time Python, JS, Java & C++ collaborative editor</span>
                  </li>
                  <li className="flex items-start gap-2.5 text-xs text-slate-700">
                    <Check className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
                    <span>Integrated live team chat and instant server-side execution</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100">
              <Link
                href="/skillsarena/aptitude"
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3.5 text-sm font-semibold text-white shadow-xs transition hover:bg-slate-800 active:scale-[0.99]"
              >
                <span>Launch SkillsArena</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* Feature Grid: 4 Placement Building Blocks */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h3 className="text-lg font-bold text-slate-900">
              Platform Features & Architecture
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              High-performance backend orchestration serving all capabilities across ports 5173 & 8000
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 mb-3">
                <BrainCircuit className="h-5 w-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">Resume Intelligence</h4>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">
                Automated parsing and multi-agent alignment against industry benchmark data.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 mb-3">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">Aptitude Testing</h4>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">
                Timed adaptive tests covering quantitative, verbal, and logical skills with verified solutions.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600 mb-3">
                <MessageSquare className="h-5 w-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">GD Simulator</h4>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">
                Synchronized turn-based rooms, microphone input analysis, and automated evaluation.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50 text-violet-600 mb-3">
                <Code2 className="h-5 w-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">Code Studio</h4>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">
                Multi-user coding in Python, JavaScript, Java, and C++ with real-time team chat.
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-200 pt-8 pb-12">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
              <Layers className="h-4 w-4 text-indigo-600" />
              <span>SkillBridge Platform</span>
              <span className="text-slate-300">|</span>
              <span>Frontend: 5173</span>
              <span className="text-slate-300">|</span>
              <span>Backend Engine: 8000</span>
            </div>

            <div className="flex items-center gap-4 text-xs font-semibold text-slate-600">
              <Link href="/careerarena" className="hover:text-indigo-600 transition">
                CareerArena
              </Link>
              <Link href="/skillsarena/aptitude" className="hover:text-indigo-600 transition">
                Aptitude
              </Link>
              <Link href="/skillsarena/gd-room" className="hover:text-indigo-600 transition">
                GD Arena
              </Link>
              <Link href="/skillsarena/code-arena" className="hover:text-indigo-600 transition">
                Code Arena
              </Link>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
