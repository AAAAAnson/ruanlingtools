'use client';

import { motion } from 'framer-motion';
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';
import { buttonAnimations } from '@/lib/animations';

interface PixelButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'onAnimationStart' | 'onDragStart' | 'onDragEnd' | 'onDrag'> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: ReactNode;
}

export function PixelButton({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  disabled,
  className = '',
  ...props
}: PixelButtonProps) {
  const baseClass = 'pixel-btn no-select';
  const variantClass = `pixel-btn-${variant}`;
  const sizeClass = `pixel-btn-${size}`;
  const combinedClass = `${baseClass} ${variantClass} ${sizeClass} ${className}`;

  return (
    <motion.button
      className={combinedClass}
      whileHover={!disabled && !loading ? buttonAnimations.hover : undefined}
      whileTap={!disabled && !loading ? buttonAnimations.tap : undefined}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin inline-block" />
      ) : (
        <>
          {icon && <span className="inline-block mr-2">{icon}</span>}
          {children}
        </>
      )}
    </motion.button>
  );
}
