import type { Metadata } from "next";
import CareerArenaClient from "./CareerArenaClient";

export const metadata: Metadata = {
  title: "CareerArena | SkillBridge Career Intelligence",
  description: "AI Resume Parsing, Target Role Readiness Scoring, and Multi-Agent Career Calibration.",
};

export default function CareerArenaPage() {
  return <CareerArenaClient />;
}
