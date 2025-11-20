/**
 * Framer Motion Animation Presets
 */

import { Variants } from 'framer-motion';

export const buttonAnimations = {
  hover: {
    scale: 1.05,
    boxShadow: '0 0 20px currentColor',
    transition: { duration: 0.2 },
  },
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 },
  },
};

export const pageTransitions: Variants = {
  initial: { opacity: 1, y: 0 },  // Changed: start visible to prevent blank page
  animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
};

export const fadeAnimations: Variants = {
  initial: { opacity: 1 },  // Changed: start visible
  animate: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

export const slideAnimations = {
  fromTop: {
    initial: { y: -100, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -100, opacity: 0 },
  },
  fromBottom: {
    initial: { y: 100, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: 100, opacity: 0 },
  },
  fromLeft: {
    initial: { x: -100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 },
  },
  fromRight: {
    initial: { x: 100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 100, opacity: 0 },
  },
};

export const scaleAnimations: Variants = {
  initial: { scale: 1, opacity: 1 },  // Changed: start visible
  animate: { scale: 1, opacity: 1, transition: { duration: 0.3 } },
  exit: { scale: 0.8, opacity: 0, transition: { duration: 0.2 } },
};

export const cardHoverAnimation = {
  rest: { scale: 1, y: 0 },
  hover: { scale: 1.02, y: -4 },
};

export const listContainerAnimation: Variants = {
  hidden: { opacity: 1 },  // Changed: start visible
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

export const listItemAnimation: Variants = {
  hidden: { opacity: 1, y: 0 },  // Changed: start visible
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export const modalAnimations = {
  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  content: {
    initial: { scale: 0.9, opacity: 0, y: 20 },
    animate: { scale: 1, opacity: 1, y: 0 },
    exit: { scale: 0.9, opacity: 0, y: 20 },
  },
};

export const toastAnimations = {
  initial: { x: 400, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: 400, opacity: 0 },
};

export const shakeAnimation = {
  shake: {
    x: [0, -10, 10, -10, 10, 0],
    transition: { duration: 0.4 },
  },
};

export const pulseAnimation = {
  scale: [1, 1.05, 1],
  transition: {
    duration: 1,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

export const spinnerAnimation = {
  rotate: 360,
  transition: {
    duration: 1,
    repeat: Infinity,
    ease: 'linear',
  },
};
