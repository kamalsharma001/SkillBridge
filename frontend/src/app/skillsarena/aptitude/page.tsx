import type { Metadata } from "next";
import AptitudeClient from "./AptitudeClient";

export const metadata: Metadata = {
  title: "Aptitude Assessment | SkillBridge SkillsArena",
  description: "Timed technical and quantitative aptitude assessment with instant scoring and detailed step-by-step explanations.",
};

export default function AptitudePage() {
  return <AptitudeClient />;
}
