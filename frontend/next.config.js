/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  // Ensure static assets are served correctly in production
  generateEtags: false,
  compress: false,
}

module.exports = nextConfig
