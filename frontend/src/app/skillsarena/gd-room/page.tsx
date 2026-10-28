import type { Metadata } from "next";
import GDClient from "./GDClient";

export const metadata: Metadata = {
  title: "GD Arena | SkillBridge SkillsArena",
  description: "Live collaborative group discussion rooms with automated turn management, real microphone audio meters, and speech evaluation.",
};

export default function GDRoomPage() {
  return <GDClient />;
}
