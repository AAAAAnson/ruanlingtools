'use client';

import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { spinnerAnimation } from '@/lib/animations';

interface PixelLoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export function PixelLoading({ size = 'md', text }: PixelLoadingProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div animate={spinnerAnimation}>
        <Loader2 className={`text-secondary ${sizeClasses[size]}`} />
      </motion.div>
      {text && <p className="font-pixel text-sm text-secondary">{text}</p>}
    </div>
  );
}
