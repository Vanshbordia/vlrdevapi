import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight, BarChart3, Code2, Workflow } from 'lucide-react';
import { CodeBlock } from '@/components/landing/code-block';
import { CopyButton } from '@/components/landing/copy-button';
import { LandingPage, LandingSection } from '@/components/landing/landing-page';
import { createPageMetadata } from '@/lib/seo';
import { SpotlightCard } from '@/components/landing/spotlight-card';

/** Canonical route for this page, shared by the metadata and the page body. */
const PATH = '/valorant-api-python'

export const metadata: Metadata = createPageMetadata({
  title: 'Valorant API for Python (No API Key)',
  description:
    'Use VLR.gg Valorant data from Python with a typed client. Install from PyPI, skip the API key, and work with Pydantic models for matches, players, teams, and stats.',
  path: PATH,
});

const workflows = [
  {
    label: 'Script or service',
    title: 'Typed calls, no parsing',
    file: 'service.py',
    icon: Code2,
    note: 'Use the client as a context manager. The underlying HTTP session closes when you leave the block.',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    team = client.team(1034)

    for member in team.roster().players:
        print(member.ign, member.roles)`,
  },
  {
    label: 'Notebook',
    title: 'Models become rows',
    file: 'analysis.ipynb',
    icon: BarChart3,
    note: 'Pydantic models expose model_dump(), so pandas and Polars are one line away.',
    code: `import pandas as pd
import vlrdevapi

agents = vlrdevapi.player(11225).agents(timespan="90d")
rows = [agent.model_dump() for agent in agents.agents]

df = pd.DataFrame(rows)
df[["agent", "rounds", "rating", "acs"]].head()`,
  },
  {
    label: 'Async app',
    title: 'Offload the blocking call',
    file: 'app.py',
    icon: Workflow,
    note: 'The SDK is synchronous by design. Move calls to a worker with asyncio.to_thread.',
    code: `import asyncio
import vlrdevapi

async def load_series():
    return await asyncio.to_thread(
        vlrdevapi.series(542272).info
    )

info = asyncio.run(load_series())
print(info.team1.name, info.score1)`,
  },
];

export default function ValorantApiPythonPage() {
  return (
    <LandingPage
      path={PATH}
      eyebrow="Python SDK"
      headline="Valorant API for Python"
      h1={
        <>
          A Valorant API for <span className="text-fd-primary">Python</span>
        </>
      }
      subtitle="A typed Python client for Valorant esports data on VLR.gg. Install it from PyPI, call a namespace, and work with validated Pydantic models — no API key, no parser, no glue code."
      answer="VLRdevAPI is a Python SDK for VLR.gg. It installs with pip, needs no API key, and returns Pydantic models for matches, players, teams, events, series, and news."
      useCases={[
        'FastAPI services',
        'Data notebooks',
        'Discord bots',
        'Cron jobs',
        'Internal tools',
        'Analytics pipelines',
      ]}
      capabilitiesTitle="Why it feels Python-native"
      capabilities={[
        {
          label: 'Install',
          bold: 'Two commands, no setup',
          text: 'pip install vlrdevapi or uv add vlrdevapi. There is no key to configure and no separate service to run.',
        },
        {
          label: 'Types',
          bold: 'Pydantic models everywhere',
          text: 'Every response is a typed model, so autocomplete, refactoring, and static analysis work in your editor.',
        },
        {
          label: 'Errors',
          bold: 'Typed exceptions',
          text: 'NotFoundError, RateLimitError, RequestError, ParsingError, and ValidationError cover the common failure modes.',
        },
        {
          label: 'Pagination',
          bold: 'Pages handled for you',
          text: 'List endpoints expose page, total pages, and items, and can fetch every page in one call.',
        },
        {
          label: 'Networking',
          bold: 'Rate limiting and caching',
          text: 'Built-in rate limiting and an LRU response cache reduce requests and keep you within reasonable volumes.',
        },
        {
          label: 'Concurrency',
          bold: 'Sync design, thread friendly',
          text: 'Call methods directly, run independent fetches in a thread pool, or use asyncio.to_thread from an async framework.',
        },
      ]}
      quickstart={{
        title: 'Your first typed response in a few lines.',
        file: 'player_profile.py',
        intro:
          'Install the package and open a player profile. The curried player object keeps the ID attached, and every field is available in your editor.',
        steps: [
          {
            title: 'Install from PyPI.',
            text: 'pip install vlrdevapi. Python 3.11+ and an internet connection.',
          },
          {
            title: 'Open a player.',
            text: 'vlrdevapi.player(11225) binds the player ID for related calls.',
          },
          {
            title: 'Read typed fields.',
            text: 'profile.name, profile.country, and agent.rating are validated values, not strings from HTML.',
          },
        ],
        code: `import vlrdevapi

player = vlrdevapi.player(11225)
profile = player.profile()
agents = player.agents(timespan="90d")

print(profile.name, "·", profile.country)
for agent in agents.agents[:3]:
    print(agent.agent, agent.rating, agent.acs)`,
        outputLabel: 'Example output',
        output: `Ethan · United States
Kayo 1.11 199.4
Phoenix 0.89 186.9
Omen 0.89 151.9`,
      }}
      comparison={{
        title: 'Python options for Valorant data',
        headers: ['', 'VLRdevAPI', 'requests + BeautifulSoup', 'Raw HTTP requests'],
        rows: [
          ['Setup', 'pip install vlrdevapi', 'Install and write selectors', 'Install and write everything'],
          ['Parsing', 'Included', 'You write CSS selectors', 'You parse by hand'],
          ['Output', 'Typed Pydantic models', 'Raw HTML', 'Raw HTML'],
          ['Rate limiting', 'Built in', 'Your responsibility', 'Your responsibility'],
          ['Maintenance', 'Handled in the library', 'High', 'High'],
          ['API key', 'Not required', 'Not required', 'Not required'],
        ],
      }}
      faqs={[
        {
          q: 'How do I install VLRdevAPI?',
          a: 'Run pip install vlrdevapi or uv add vlrdevapi. Python 3.11 or newer is required.',
        },
        {
          q: 'Is there a Python wrapper for VLR.gg?',
          a: 'VLRdevAPI is a dedicated Python SDK for VLR.gg. It wraps the pages VLR.gg serves and returns typed objects instead of raw HTML.',
        },
        {
          q: 'Does it work with type checkers?',
          a: 'Yes. Every response is a Pydantic model with type hints, so autocomplete and static analysis work in editors like VS Code and PyCharm.',
        },
        {
          q: 'Can I use it with pandas?',
          a: 'Yes. Convert models to dictionaries or DataFrames with model_dump() and build your own analysis, or follow the pandas and Polars guides.',
        },
        {
          q: 'Can I use it in an async app?',
          a: 'The client itself is synchronous. In FastAPI or another async framework, call it with asyncio.to_thread or run independent calls in a thread pool.',
        },
        {
          q: 'Do I need an API key?',
          a: 'No. There is no key, token, or account. Install the package and start calling methods.',
        },
      ]}
      faqIntro="Installation, typing, async use, and the practical questions Python developers ask first."
      related={[
        {
          href: '/docs/installation/',
          label: 'Installation',
          desc: 'Install with pip, uv, or from source.',
        },
        {
          href: '/docs/quickstart/',
          label: 'Quickstart',
          desc: 'A hands-on tour of the main namespaces.',
        },
        {
          href: '/guides/getting-started-with-vlrdevapi/',
          label: 'Getting started guide',
          desc: 'From an empty project to your first request.',
        },
        {
          href: '/guides/player-analytics-with-pandas/',
          label: 'Player analytics with pandas',
          desc: 'Turn typed models into a DataFrame.',
        },
        {
          href: '/valorant-stats-api/',
          label: 'Valorant stats API',
          desc: 'Player, team, and match statistics in Python.',
        },
        {
          href: '/vlr-gg-api/',
          label: 'VLR.gg API for Python',
          desc: 'Why an unofficial client exists.',
        },
      ]}
    >
      <LandingSection
        eyebrow="In practice"
        title="One client, three Python workflows."
        description="The same typed response works in a script, a notebook, or an async service. These are the three patterns most projects start with."
        action={
          <Link
            href="/guides/"
            className="group inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
          >
            Browse Python guides
            <ArrowUpRight
              className="size-3.5 text-fd-primary transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        }
      >
        <div className="grid gap-3 lg:grid-cols-3">
          {workflows.map((workflow) => {
            const Icon = workflow.icon;

            return (
              <SpotlightCard key={workflow.file} className="flex h-full flex-col p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                      {workflow.label}
                    </p>
                    <h3 className="mt-2 text-[15px] font-medium tracking-tight text-white">
                      {workflow.title}
                    </h3>
                  </div>
                  <Icon className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                </div>

                <div className="mt-5 overflow-hidden border border-white/10 bg-fd-canvas">
                  <div className="flex items-center justify-between gap-3 border-b border-white/10 px-3 py-2">
                    <span className="font-mono text-[12px] text-fd-muted">{workflow.file}</span>
                    <CopyButton
                      value={workflow.code}
                      label={`Copy ${workflow.file}`}
                      className="border-white/10 bg-transparent"
                    />
                  </div>
                  <CodeBlock code={workflow.code} lineNumbers={false} />
                </div>

                <p className="mt-4 text-[12.5px] leading-relaxed text-fd-muted">
                  {workflow.note}
                </p>
              </SpotlightCard>
            );
          })}
        </div>
      </LandingSection>
    </LandingPage>
  );
}
