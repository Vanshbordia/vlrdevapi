'use client';
import { useEffect } from 'react';

/**
 * Injects a GitHub link into the docs sidebar footer, inline with the Theme Toggle button.
 * This avoids replacing the default footer provided by DocsLayout and instead augments it.
 */
export function SidebarFooterGithub() {
  useEffect(() => {
    try {
      // Find the theme toggle button rendered by the layout
      const toggleBtn = document.querySelector('[data-theme-toggle]') as HTMLElement | null;
      if (!toggleBtn) return;

      const container = toggleBtn.closest('div');
      if (!container) return;

      // Avoid duplicate insertion
      if (container.querySelector('[data-github-link]')) return;

      // Create GitHub anchor element
      const a = document.createElement('a');
      a.href = 'https://github.com/Vanshbordia/vlrdevapi';
      a.target = '_blank';
      a.rel = 'noreferrer noopener';
      a.setAttribute('aria-label', 'GitHub Repository');
      a.setAttribute('data-github-link', '');
      a.className = [
        'inline-flex items-center justify-center rounded-full border',
        'p-0 ms-2', // small spacing from the left items, keep toggle aligned to the right via ms-auto on toggle
        'text-fd-muted-foreground hover:text-fd-foreground',
      ].join(' ');

      // Icon wrapper styles to match Theme Toggle icon sizing
      a.innerHTML = `
        <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden>
          <path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.53 2.87 8.36 6.85 9.72.5.1.68-.22.68-.49 0-.24-.01-.87-.01-1.7-2.78.62-3.37-1.36-3.37-1.36-.45-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06 .9 1.56 2.36 1.11 2.94.85.09-.67.35-1.11.63-1.36-2.22-.26-4.56-1.14-4.56-5.08 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.32.1-2.75 0 0 .85-.28 2.79 1.05a9.3 9.3 0 0 1 2.54-.35c.86 0 1.73.12 2.54.35 1.94-1.33 2.79-1.05 2.79-1.05.55 1.43.2 2.49.1 2.75.64.72 1.03 1.64 1.03 2.76 0 3.95-2.34 4.82-4.57 5.08.36.32.68.94.68 1.9 0 1.36-.01 2.45-.01 2.78 0 .27.18.59.69.49A10.03 10.03 0 0 0 22 12.26C22 6.58 17.52 2 12 2z"/>
        </svg>
      `;

      // Insert the link before the theme toggle, so the toggle stays aligned to the right via ms-auto
      container.insertBefore(a, toggleBtn);
    } catch {
      // no-op
    }
  }, []);

  return null;
}
