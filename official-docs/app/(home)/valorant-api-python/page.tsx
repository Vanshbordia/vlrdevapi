import type { Metadata } from 'next';
import { LandingPage } from '@/components/landing/landing-page';
import { canonicalUrl } from '@/lib/shared';

export const metadata: Metadata = {
  title: 'Valorant API for Python (No API Key)',
  description:
    'Use the VLR.gg Valorant API from Python. VLRdevAPI installs from PyPI, needs no API key, and returns typed Pydantic models for matches, players, and teams.',
  alternates: { canonical: canonicalUrl('/valorant-api-python/') },
};

export default function ValorantApiPythonPage() {
  return (
    <LandingPage
      path="/valorant-api-python"
      eyebrow="Python"
      headline="Valorant API for Python"
      h1={
        <>
          A Valorant API for <span className="text-fd-primary">Python</span>
        </>
      }
      subtitle="A typed Python client for Valorant esports data from VLR.gg. Install it, import it, and work with matches, players, teams, and events as Pydantic models."
      answer="VLRdevAPI is the Python client for Valorant esports data on VLR.gg. It installs from PyPI with pip, needs no API key, and returns typed models with full editor support."
      capabilitiesTitle="What makes it Python-native"
      capabilities={[
        {
          label: 'Install',
          bold: 'Two commands, no setup',
          text: 'pip install vlrdevapi or uv add vlrdevapi. There are no native dependencies and no key to configure.',
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
        intro:
          'Install the package and fetch a player profile. Every field is typed, so the data is ready to use without manual parsing.',
        code: `import vlrdevapi

profile = vlrdevapi.player(438).profile()
print(f"{profile.name}: {', '.join(a.agent for a in profile.top_agents[:3])}")`,
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
          q: 'Is it synchronous?',
          a: 'Yes. Each method is a blocking call. For concurrency, run independent calls in a thread pool, or use asyncio.to_thread from an async framework.',
        },
        {
          q: 'Do I need an API key?',
          a: 'No. There is no key, token, or account. Install the package and start calling methods.',
        },
      ]}
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
    />
  );
}
