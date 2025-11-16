'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { ReactNode, useEffect } from 'react';
import { modalAnimations } from '@/lib/animations';

interface PixelModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export function PixelModal({ isOpen, onClose, title, children, size = 'md' }: PixelModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            {...modalAnimations.backdrop}
            className="fixed inset-0 bg-black/80 z-50"
            onClick={onClose}
          />
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              {...modalAnimations.content}
              className={`pixel-card w-full ${sizeClasses[size]}`}
              onClick={(e) => e.stopPropagation()}
            >
              {title && (
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-pixel text-xl text-primary">{title}</h2>
                  <button onClick={onClose} className="hover:opacity-70 transition-opacity">
                    <X className="w-6 h-6" />
                  </button>
                </div>
              )}
              {children}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
