import { Header } from '@/components/home/header';
import Link from 'next/link';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      {children}
      <footer className="border-t">
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
            <div className="sm:col-span-2 lg:col-span-2">
              <h3 className="text-lg font-bold text-foreground">VLRdevAPI</h3>
              <p className="mt-2 max-w-md text-sm leading-snug text-muted-foreground">
                A type-safe Python SDK for the Valorant esports data API from VLR.gg, built by{' '}
                <Link href="https://riftwatch.org" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground transition-colors">RiftWatch</Link>.
                Fetch match results, player stats, team rosters, and tournament brackets through a fully typed Python interface.
              </p>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-widest text-foreground">Docs</h4>
              <ul className="mt-4 flex flex-col gap-3">
                <li><Link href="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Getting Started</Link></li>
                <li><Link href="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">API Reference</Link></li>
                <li><Link href="/guides" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Guides</Link></li>
                <li><Link href="/blog" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Blog</Link></li>
                <li><Link href="/changelog" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Changelog</Link></li>
                <li><Link href="/faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</Link></li>
                <li><Link href="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Installation</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-widest text-foreground">Links</h4>
              <ul className="mt-4 flex flex-col gap-3">
                <li><Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</Link></li>
                <li><Link href="https://pypi.org/project/vlrdevapi/" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">PyPI</Link></li>
                <li><Link href="https://vlr.gg" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">VLR.gg</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
            <p className="text-xs text-muted-foreground">
              &copy; {new Date().getFullYear()} VLRdevAPI by{' '}
              <Link href="https://riftwatch.org" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground transition-colors">RiftWatch</Link>. Not affiliated with Riot Games or VLR.gg.
            </p>
            <p className="text-xs text-muted-foreground">
              Built with Python &middot; Open source on{' '}
              <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground transition-colors">GitHub</Link> &middot;{' '}
              <Link href="https://riftwatch.org" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground transition-colors">RiftWatch</Link>
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
