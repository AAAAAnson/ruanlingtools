import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Soft Collar Toolbox 2.0',
  description: 'A pixel art themed toolbox for image, PDF, and text processing',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="preconnect"
          href="https://fonts.loli.net"
          crossOrigin="anonymous"
        />
        <link
          rel="stylesheet"
          href="https://fonts.loli.net/css2?family=Press+Start+2P&family=Roboto:wght@300;400;500;700&display=swap"
          crossOrigin="anonymous"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
