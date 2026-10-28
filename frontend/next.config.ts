import type { NextConfig } from "next";
import os from "os";

// Discover all local network IPv4 addresses so devices across Wi-Fi / LAN are allowed without 403 Forbidden
const allowedHosts: string[] = [
  "localhost",
  "127.0.0.1",
  "localhost:5173",
  "127.0.0.1:5173",
  "172.22.220.134",
  "172.22.220.134:5173",
  "*.local",
];

try {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name] || []) {
      if (net.family === "IPv4" && !net.internal) {
        allowedHosts.push(net.address);
        allowedHosts.push(`${net.address}:5173`);
      }
    }
  }
} catch {
  // Ignore interface lookup failure
}

const nextConfig: NextConfig = {
  devIndicators: false,
  allowedDevOrigins: allowedHosts,
};

export default nextConfig;
