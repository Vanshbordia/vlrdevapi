'use client';
import React, { useEffect, useRef } from 'react';
import { CanvasRevealEffect } from '@/components/ui/canvas-reveal-effect';

interface HowItWorksCardProps {
  colors: number[][];
  icon: React.ReactNode;
}

export function HowItWorksCard({ colors, icon }: HowItWorksCardProps) {
  const [visible, setVisible] = React.useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisible(true);
      },
      { threshold: 0.3 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className="relative flex h-full w-full items-center justify-center overflow-hidden  bg-background">
      {visible && (
        <div className="absolute inset-0">
          <CanvasRevealEffect
            animationSpeed={3}
            containerClassName="bg-black"
            colors={colors}
            dotSize={2}
          />
        </div>
      )}
      <div className="relative z-20 flex w-full items-center justify-center p-4 sm:p-8">
        {icon}
      </div>
    </div>
  );
}
