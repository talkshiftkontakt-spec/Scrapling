import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:3101";

const nextConfig: NextConfig = {
  typedRoutes: true,
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "3101",
        pathname: "/static/**"
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "3101",
        pathname: "/static/**"
      }
    ]
  },
  env: {
    NEXT_PUBLIC_API_URL: apiUrl
  },
  async rewrites() {
    return [
      {
        source: "/api-proxy/:path*",
        destination: `${apiUrl}/:path*`
      },
      {
        source: "/static/:path*",
        destination: `${apiUrl}/static/:path*`
      }
    ];
  }
};

export default nextConfig;
