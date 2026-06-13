import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  // Produce a self-contained server build for Docker/Railway deploys.
  output: "standalone",
  // Pin the workspace root to this folder (a stray lockfile exists in the home dir).
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
