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
        <div className="flex items-center gap-2 mb-4">
          {icon && <div className="text-primary">{icon}</div>}
          <h3 className="font-pixel text-lg text-primary">
            {title}
          </h3>
        </div>
      )}
      {children}
    </motion.div>
  );
}
