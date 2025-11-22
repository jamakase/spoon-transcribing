import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: __dirname,
  },
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://api.transcribe.aprivai.com/:path*',
      },
    ];
  },
};

export default nextConfig;
