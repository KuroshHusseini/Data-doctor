/** @type {import('next').NextConfig} */
const nextConfig = {
  // App directory is now stable in Next.js 14, no need for experimental flag
  sassOptions: {
    includePaths: ["./src/styles"],
  },
  images: {
    domains: ["localhost"],
  },
};

module.exports = nextConfig;
