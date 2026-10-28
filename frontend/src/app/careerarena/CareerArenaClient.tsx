"use client";

import CareerArena from "../components/CareerArena";
import { getApiBase } from "../utils/apiBase";

export default function CareerArenaClient() {
  return <CareerArena apiBase={getApiBase()} />;
}
