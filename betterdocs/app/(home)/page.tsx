import Link from 'next/link';
import { InstallationCommand } from '@/components/installation-command';

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-background text-foreground selection:bg-primary/20 font-sans">
      {/* Hero Section */}
      <section className="relative flex w-full max-w-9xl flex-col items-center justify-center px-4 py-24 text-center md:py-32">
        {/* Grid Background */}
        <div className="absolute inset-0 -z-10 h-full w-full bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>

        <div className="mb-8 flex flex-wrap items-center justify-center gap-3">
          <div className="inline-flex items-center border border-border bg-background/50 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-sm">
            <span className="mr-2 inline-block h-1.5 w-1.5 bg-green-500"></span>
            v1.3.0
          </div>
          <div className="inline-flex items-center border border-border bg-background/50 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-sm">
            <span className="mr-2">🐍</span>
            Python 3.11+
          </div>
        </div>

        <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl text-foreground">
          The Ultimate Python Library <br className="hidden sm:block" />
          for <span className="text-primary">VLR.gg</span>
        </h1>

        <p className="mb-10 max-w-2xl text-lg text-muted-foreground sm:text-xl">
          Access Valorant esports data with a clean, type-safe Python API.
          Get tournament info, match schedules, player stats, and more in seconds.
        </p>

        <div className="flex flex-col gap-4 sm:flex-row">
          <Link
            href="/docs"
            className="inline-flex h-11 items-center justify-center bg-primary px-8 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Read the Docs
          </Link>
          <a
            href="https://github.com/vanshbordia/vlrdevapi"
            target="_blank"
            rel="noreferrer"
            className="group inline-flex h-11 items-center justify-center border border-input bg-background px-8 text-sm font-medium shadow-sm transition-all duration-300 hover:bg-accent hover:text-accent-foreground hover:scale-105 hover:shadow-md focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="mr-2 transition-transform duration-300 group-hover:rotate-12"
            >
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            View on GitHub
          </a>
        </div>

        {/* Installation Commands */}
        <div className="mt-12 flex w-full max-w-2xl flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <InstallationCommand command="pip install vlrdevapi" label="pip" />
          <InstallationCommand command="uv add vlrdevapi" label="uv" />
        </div>
      </section>

      {/* Features Grid */}
      <section className="w-full max-w-6xl px-4 py-16 border-t border-border/40">
        <div className="grid gap-px bg-border/50 sm:grid-cols-2 lg:grid-cols-4 border border-border/50">
          <FeatureCard
            title="Complete Data Access"
            description="Events, matches, players, teams, series, and search functionality at your fingertips."
            icon={<DatabaseIcon />}
          />
          <FeatureCard
            title="Type-Safe"
            description="Frozen Python dataclasses with rich type hints for a better development experience."
            icon={<ShieldCheckIcon />}
          />
          <FeatureCard
            title="Production-Ready"
            description="Built-in error handling, retry logic, and rate limiting for robust applications."
            icon={<ServerIcon />}
          />
          <FeatureCard
            title="Easy to Use"
            description="Simple, intuitive API design that lets you focus on building, not scraping."
            icon={<SparklesIcon />}
          />
        </div>
      </section>

      {/* Code Showcase */}
      <section className="w-full max-w-6xl px-4 py-16 border-t border-border/40">
        <div className="grid gap-0 border border-border lg:grid-cols-2">
          {/* Code Block */}
          <div className="bg-card text-card-foreground overflow-hidden flex flex-col h-full border-r border-border">
            <div className="flex items-center justify-between border-b border-border bg-muted/30 px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 bg-red-500/80"></div>
                <div className="h-3 w-3 bg-yellow-500/80"></div>
                <div className="h-3 w-3 bg-green-500/80"></div>
                <span className="ml-2 text-xs text-muted-foreground font-mono">example.py</span>
              </div>
              <span className="text-xs font-medium text-muted-foreground">Input</span>
            </div>
            <div className="overflow-x-auto bg-[#0d1117] p-6 text-sm flex-1">
              <pre className="font-mono leading-relaxed">
                <code className="text-gray-300">
                  <span className="text-[#ff7b72]">import</span> vlrdevapi <span className="text-[#ff7b72]">as</span> vlr{'\n\n'}
                  <span className="text-[#8b949e]"># Search for anything</span>{'\n'}
                  results = vlr.search.search(<span className="text-[#a5d6ff]">"nrg"</span>){'\n'}
                  <span className="text-[#d2a8ff]">print</span>(f<span className="text-[#a5d6ff]">"Found &#123;results.total_results&#125; results"</span>){'\n\n'}
                  <span className="text-[#8b949e]"># Get upcoming matches</span>{'\n'}
                  matches = vlr.matches.upcoming(limit=<span className="text-[#79c0ff]">5</span>){'\n'}
                  <span className="text-[#ff7b72]">for</span> match <span className="text-[#ff7b72]">in</span> matches:{'\n'}
                  {'    '}<span className="text-[#d2a8ff]">print</span>(f<span className="text-[#a5d6ff]">"&#123;match.team1.name&#125; vs &#123;match.team2.name&#125;"</span>)
                </code>
              </pre>
            </div>
          </div>

          {/* Output Block */}
          <div className="bg-card text-card-foreground overflow-hidden flex flex-col h-full">
            <div className="flex items-center justify-between border-b border-border bg-muted/30 px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 bg-red-500/80"></div>
                <div className="h-3 w-3 bg-yellow-500/80"></div>
                <div className="h-3 w-3 bg-green-500/80"></div>
                <span className="ml-2 text-xs text-muted-foreground font-mono">terminal</span>
              </div>
              <span className="text-xs font-medium text-muted-foreground">Output</span>
            </div>
            <div className="overflow-x-auto bg-[#0d1117] p-6 text-sm flex-1">
              <pre className="font-mono leading-relaxed">
                <code className="text-gray-300">
                  <span className="text-green-400">$ python example.py</span>{'\n'}
                  Found 42 results{'\n'}
                  NRG vs Sentinels{'\n'}
                  Cloud9 vs 100 Thieves{'\n'}
                  Leviatán vs KRÜ Esports{'\n'}
                  G2 Esports vs Evil Geniuses{'\n'}
                  LOUD vs FURIA
                </code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full max-w-6xl px-4 py-12 text-center border-t border-border/40">
        <p className="text-sm text-muted-foreground mb-4">
          &copy; {new Date().getFullYear()} vlrdevapi. Open source under MIT License.
        </p>
        <div className="flex gap-6 text-sm text-muted-foreground justify-center">
          <a href="https://github.com/vanshbordia/vlrdevapi" className="hover:text-foreground transition-colors">GitHub</a>
          <a href="https://pypi.org/project/vlrdevapi/" className="hover:text-foreground transition-colors">PyPI</a>
          <Link href="/docs" className="hover:text-foreground transition-colors">Documentation</Link>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <div className="group bg-card p-8 text-card-foreground transition-colors hover:bg-muted/50">
      <div className="mb-4 inline-flex h-10 w-10 items-center justify-center bg-primary/10 text-primary">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}

function DatabaseIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5V19A9 3 0 0 0 21 19V5" />
      <path d="M3 12A9 3 0 0 0 21 12" />
    </svg>
  );
}

function ShieldCheckIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67 0C6.5 20.5 3 18 3 13V7l9-4 9 4Z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

function ServerIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect width="20" height="8" x="2" y="2" rx="2" ry="2" />
      <rect width="20" height="8" x="2" y="14" rx="2" ry="2" />
      <line x1="6" x2="6.01" y1="6" y2="6" />
      <line x1="6" x2="6.01" y1="18" y2="18" />
    </svg>
  );
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M9.93 5.53A6.37 6.37 0 0 0 12 2c.42 0 .83.04 1.24.11" />
      <path d="M19.07 11.53A6.37 6.37 0 0 0 22 12c0 .42-.04.83-.11 1.24" />
      <path d="M14.07 18.47A6.37 6.37 0 0 0 12 22c-.42 0-.83-.04-1.24-.11" />
      <path d="M4.93 12.47A6.37 6.37 0 0 0 2 12c0-.42.04-.83.11-1.24" />
      <path d="M12 8a2 2 0 0 1 2 2c0 .26-.05.5-.13.73L12 12l-1.87-1.27A2 2 0 0 1 10 10a2 2 0 0 1 2-2Z" />
      <path d="M12 14a2 2 0 0 1-2-2c0-.26.05-.5.13-.73L12 10l1.87 1.27A2 2 0 0 1 14 12a2 2 0 0 1-2 2Z" />
    </svg>
  );
}

function LayersIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z" /><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65" /><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65" /></svg>
  );
}
