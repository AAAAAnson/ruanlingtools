'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Image, FileText, File, Wand2, Youtube } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const navItems = [
  { href: '/image', label: 'Image Tools', icon: Image },
  { href: '/text', label: 'Text Tools', icon: FileText },
  { href: '/pdf', label: 'PDF Tools', icon: File },
  { href: '/ai', label: 'AI Tools', icon: Wand2 },
  { href: '/youtube', label: 'YouTube', icon: Youtube },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="pixel-border border-b-2 bg-dark sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-primary pixel-border flex items-center justify-center group-hover:pixel-glow transition-all">
              <span className="font-pixel text-xs text-dark">ST</span>
            </div>
            <h1 className="font-pixel text-sm hidden sm:block text-gradient">
              Soft Collar Toolbox
            </h1>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-4 py-2 font-pixel text-xs text-secondary hover:text-primary hover:pixel-glow transition-all flex items-center gap-2"
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden lg:inline">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-secondary hover:text-primary transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.nav
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden overflow-hidden border-t-2 border-[#333344] mt-2"
            >
              <div className="py-4 space-y-2">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 font-pixel text-xs text-secondary hover:text-primary hover:bg-darker transition-all"
                    >
                      <Icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </motion.nav>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
}
