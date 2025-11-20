/**
 * Framer Motion Animation Presets
 * Optimized for performance - minimal animations, GPU-accelerated properties only
 */

import { Variants } from 'framer-motion';

// Optimized button animations - removed box-shadow (poor performance)
export const buttonAnimations = {
  hover: {
    scale: 1.02,
    transition: {
      duration: 0.15,
      ease: 'easeOut',
    },
  },
  tap: {
    scale: 0.98,
    transition: {
      duration: 0.1,
      ease: 'easeOut',
    },
  },
};

// Simplified page transitions - no initial animation to prevent flash
export const pageTransitions: Variants = {
  initial: { opacity: 1 },
  animate: { opacity: 1 },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

// Simplified fade - no initial animation
export const fadeAnimations: Variants = {
  initial: { opacity: 1 },
  animate: { opacity: 1 },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

// Optimized slide animations - shorter distances, faster transitions
export const slideAnimations = {
  fromTop: {
    initial: { y: -20, opacity: 0 },
    animate: { y: 0, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
    exit: { y: -20, opacity: 0, transition: { duration: 0.15 } },
  },
  fromBottom: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
    exit: { y: 20, opacity: 0, transition: { duration: 0.15 } },
  },
  fromLeft: {
    initial: { x: -20, opacity: 0 },
    animate: { x: 0, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
    exit: { x: -20, opacity: 0, transition: { duration: 0.15 } },
  },
  fromRight: {
    initial: { x: 20, opacity: 0 },
    animate: { x: 0, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
    exit: { x: 20, opacity: 0, transition: { duration: 0.15 } },
  },
};

// Simplified scale - no initial animation
export const scaleAnimations: Variants = {
  initial: { scale: 1, opacity: 1 },
  animate: { scale: 1, opacity: 1 },
  exit: { scale: 0.95, opacity: 0, transition: { duration: 0.15 } },
};

// Optimized card hover - subtle effect, GPU-accelerated only
export const cardHoverAnimation = {
  rest: {
    scale: 1,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
  hover: {
    scale: 1.01,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

// No animations for lists - they should appear instantly for better UX
export const listContainerAnimation: Variants = {
  hidden: { opacity: 1 },
  show: { opacity: 1 },
};

export const listItemAnimation: Variants = {
  hidden: { opacity: 1 },
  show: { opacity: 1 },
};

// Optimized modal animations - faster, smoother
export const modalAnimations = {
  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.15 } },
    exit: { opacity: 0, transition: { duration: 0.15 } },
  },
  content: {
    initial: { scale: 0.95, opacity: 0 },
    animate: { scale: 1, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
    exit: { scale: 0.95, opacity: 0, transition: { duration: 0.15 } },
  },
};

// Optimized toast animations - shorter distance
export const toastAnimations = {
  initial: { x: 100, opacity: 0 },
  animate: { x: 0, opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
  exit: { x: 100, opacity: 0, transition: { duration: 0.15 } },
};

// Optimized shake - shorter, faster
export const shakeAnimation = {
  shake: {
    x: [0, -5, 5, -5, 5, 0],
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Subtle pulse animation
export const pulseAnimation = {
  scale: [1, 1.02, 1],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

// Fast spinner
export const spinnerAnimation = {
  rotate: 360,
  transition: {
    duration: 0.8,
    repeat: Infinity,
    ease: 'linear',
  },
};
