import type { Metadata } from "next";
import CodeClient from "./CodeClient";

export const metadata: Metadata = {
  title: "Code Arena | SkillBridge SkillsArena",
  description: "Real-time collaborative code editor supporting Python, JavaScript, Java, and C++ with multi-language execution and live team chat.",
};

export default function CodeArenaPage() {
  return <CodeClient />;
}
