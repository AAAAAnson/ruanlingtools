'use client';

import { motion } from 'framer-motion';
import { Construction, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelCard } from '@/components/ui/PixelCard';
import { pageTransitions } from '@/lib/animations';

interface ComingSoonProps {
  title?: string;
  message?: string;
  estimatedRelease?: string;
}

export function ComingSoon({
  title = "Coming Soon",
  message = "This feature is currently under development and will be available soon.",
  estimatedRelease
}: ComingSoonProps) {
  return (
    <motion.div
      variants={pageTransitions}
      initial="initial"
      animate="animate"
      exit="exit"
      className="min-h-[60vh] flex items-center justify-center p-4"
    >
      <PixelCard className="max-w-2xl w-full text-center">
        <Construction className="w-24 h-24 mx-auto mb-6 text-accent" />
        
        <h1 className="font-pixel text-2xl md:text-3xl mb-4 text-primary">
          {title}
        </h1>
        
        <p className="text-gray-400 mb-6 max-w-md mx-auto">
          {message}
        </p>
        
        {estimatedRelease && (
          <div className="mb-6 px-4 py-2 bg-darker border-2 border-secondary inline-block">
            <p className="font-pixel text-xs text-secondary">
              Estimated Release: {estimatedRelease}
            </p>
          </div>
        )}
        
        <div className="space-y-4">
          <h3 className="font-pixel text-sm text-accent mb-2">What to expect:</h3>
          <ul className="text-sm text-gray-400 space-y-2 text-left max-w-md mx-auto">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-secondary" />
              Pixel art themed interface
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-secondary" />
              Fast and efficient processing
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-secondary" />
              Privacy-focused local processing
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-secondary" />
              Free to use forever
            </li>
          </ul>
        </div>
        
        <div className="mt-8">
          <Link href="/">
            <PixelButton variant="secondary" icon={<ArrowLeft className="w-4 h-4" />}>
              Back to Home
            </PixelButton>
          </Link>
        </div>
      </PixelCard>
    </motion.div>
  );
}
