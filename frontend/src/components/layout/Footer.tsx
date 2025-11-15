'use client';

import { Github, Heart } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="pixel-border border-t-2 bg-dark mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="font-pixel text-sm text-primary mb-4">About</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              A collection of useful tools for image processing, PDF manipulation, 
              and text formatting. Built with pixel art aesthetics.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-pixel text-sm text-secondary mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <a href="/image" className="text-sm text-gray-400 hover:text-primary transition-colors">
                  Image Tools
                </a>
              </li>
              <li>
                <a href="/text" className="text-sm text-gray-400 hover:text-primary transition-colors">
                  Text Tools
                </a>
              </li>
              <li>
                <a href="/pdf" className="text-sm text-gray-400 hover:text-primary transition-colors">
                  PDF Tools
                </a>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h3 className="font-pixel text-sm text-accent mb-4">Info</h3>
            <p className="text-sm text-gray-400 mb-3">
              Version 0.1.0 (P0 Phase)
            </p>
            <p className="text-sm text-gray-400 flex items-center gap-2">
              Made with <Heart className="w-4 h-4 text-danger inline" /> for productivity
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-6 border-t-2 border-[#333344] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-gray-500">
            © {currentYear} Soft Collar Toolbox. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-primary transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
