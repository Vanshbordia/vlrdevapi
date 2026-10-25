import Link from 'next/link';
import { Brand } from './brand';
import { GithubIcon } from './github-icon';
import { DocsCtaLink, SiteNavLinks } from './site-nav-links';
import { MobileNav } from './mobile-nav';
import { WhyMenu } from './why-menu';
import { project } from '@/lib/project';

/**
 * Site header.
 *
 * A Server Component: only the active-route highlighting, the "Why"
 * disclosure and the mobile drawer are client islands.
 */
export function SiteHeader() {
  return (
    <>
      <a
        href="#main"
        className="fixed left-4 top-3 z-[70] -translate-y-20 bg-white px-4 py-2 text-sm font-medium text-black transition-transform focus:translate-y-0"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-50 border-b border-white/10 bg-black/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-6 px-5 sm:px-8">
          <div className="flex items-center gap-3">
            <Brand />
            <Link
              href="/changelog/"
              title={`View ${project.version} release notes`}
              className="hidden border border-white/15 px-2 py-0.5 font-mono text-[12px] tracking-wide text-white/50 transition-colors hover:border-fd-primary/50 hover:text-white sm:inline"
            >
              v{project.version}
            </Link>
          </div>

          <nav aria-label="Main navigation" className="hidden flex-1 items-center gap-1 lg:flex">
            <SiteNavLinks />
            <WhyMenu />
          </nav>

          <div className="ml-auto hidden items-center gap-2.5 lg:flex">
            <Link
              href="https://github.com/vanshbordia/vlrdevapi"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="VLRdevAPI on GitHub"
              className="inline-flex size-9 items-center justify-center border border-white/10 text-white/70 transition-colors hover:border-white/25 hover:text-white"
            >
              <GithubIcon className="size-4" />
            </Link>
            <Link
              href="https://pypi.org/project/vlrdevapi/"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 text-[13.5px] font-medium text-white/70 transition-colors hover:text-white"
            >
              PyPI
            </Link>
            <DocsCtaLink />
          </div>

          <MobileNav />
        </div>
      </header>
    </>
  );
}
