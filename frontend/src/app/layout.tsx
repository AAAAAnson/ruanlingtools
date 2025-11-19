import type { Metadata } from 'next';
import { Press_Start_2P, Roboto } from 'next/font/google';
import '@/styles/globals.css';

const pressStart2P = Press_Start_2P({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-pixel',
  display: 'swap',
});

const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

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
    <html lang="en" className={`${pressStart2P.variable} ${roboto.variable}`}>
      <body className={roboto.className}>{children}</body>
    </html>
  );
}
