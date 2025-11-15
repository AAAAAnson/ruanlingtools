'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';
import { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface PixelToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
  duration?: number;
}

export function PixelToast({ type, message, onClose, duration = 3000 }: PixelToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const config = {
    success: { icon: CheckCircle, color: '#51CF66' },
    error: { icon: XCircle, color: '#FF6B6B' },
    warning: { icon: AlertCircle, color: '#FFD93D' },
    info: { icon: Info, color: '#4ECDC4' },
  };

  const Icon = config[type].icon;

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      className="pixel-card flex items-center gap-3 min-w-[300px] shadow-lg"
      style={{ borderColor: config[type].color }}
    >
      <Icon style={{ color: config[type].color }} className="w-5 h-5" />
      <p className="flex-1 text-sm">{message}</p>
      <button onClick={onClose} className="hover:opacity-70 transition-opacity">
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
}
