'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Image, FileText, File, Wand2, Search, Home, Settings } from 'lucide-react';
import Link from 'next/link';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/image', label: 'Image Tools', icon: Image },
  { href: '/text', label: 'Text Tools', icon: FileText },
  { href: '/pdf', label: 'PDF Tools', icon: File },
  { href: '/ai', label: 'AI Tools', icon: Wand2 },
  { href: '/search', label: 'Search Tools', icon: Search },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50 md:hidden"
          />

          {/* Sidebar */}
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed top-0 left-0 h-full w-64 bg-dark pixel-border border-r-2 z-50 md:hidden overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b-2 border-[#333344]">
              <h2 className="font-pixel text-sm text-primary">Menu</h2>
              <button
                onClick={onClose}
                className="p-2 hover:text-primary transition-colors"
                aria-label="Close sidebar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="p-4">
              <ul className="space-y-2">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={onClose}
                        className="flex items-center gap-3 px-4 py-3 pixel-card hover:border-primary transition-all"
                      >
                        <Icon className="w-5 h-5 text-secondary" />
                        <span className="font-pixel text-xs">{item.label}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>

            {/* Footer */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t-2 border-[#333344]">
              <p className="text-xs text-gray-500 text-center">
                Version 0.1.0
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
