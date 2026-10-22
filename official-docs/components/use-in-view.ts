'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Tracks whether an element is in the viewport.
 *
 * The observer is attached from a ref callback (which runs during commit)
 * rather than an effect, so no state is set synchronously inside an effect
 * body. Callers use this to pause animations that would otherwise keep
 * running while the element is off screen.
 */
export function useInView<T extends HTMLElement>(threshold = 0.2) {
  const [visible, setVisible] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const ref = useCallback(
    (node: T | null) => {
      observerRef.current?.disconnect();
      observerRef.current = null;

      if (!node) return;

      if (!('IntersectionObserver' in window)) {
        setVisible(true);
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => setVisible(entries.some((entry) => entry.isIntersecting)),
        { threshold },
      );

      observer.observe(node);
      observerRef.current = observer;
    },
    [threshold],
  );

  useEffect(() => () => observerRef.current?.disconnect(), []);

  return { ref, visible };
}
