'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cardHoverAnimation } from '@/lib/animations';

interface PixelCardProps {
  children: ReactNode;
  title?: string;
  icon?: ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

export function PixelCard({
  children,
  title,
  icon,
  className = '',
  hoverable = true,
  onClick,
}: PixelCardProps) {
  const baseClass = 'pixel-card';
  const combinedClass = `${baseClass} ${className}`;

  return (
    <motion.div
      className={combinedClass}
      initial="rest"
      whileHover={hoverable ? "hover" : undefined}
      variants={cardHoverAnimation}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {title && (
        <h3 className="font-pixel text-lg mb-4 text-primary flex items-center gap-2">
          {icon && <span className="inline-flex">{icon}</span>}
          {title}
        </h3>
      )}
      {children}
    </motion.div>
  );
}
