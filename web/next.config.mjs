/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath: "/intent-mandate-guard",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
