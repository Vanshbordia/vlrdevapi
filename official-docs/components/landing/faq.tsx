import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { FaqAccordion } from '@/components/marketing/faq-accordion';

const faqs = [
  {
    question: 'Is VLRdevAPI an official VLR.gg API?',
    answer:
      'No. VLRdevAPI is an independent, open-source Python client and MCP server that reads publicly available pages on VLR.gg and converts them into typed models. It is not affiliated with, endorsed by, or supported by VLR.gg or Riot Games.',
  },
  {
    question: 'Can I connect VLRdevAPI to Claude Desktop, Cursor, or AI coding agents?',
    answer:
      'Yes! VLRdevAPI includes a native Model Context Protocol (MCP) server. Run "claude mcp add vlrdevapi -- uvx --from \\"vlrdevapi[mcp]\\" vlrdevapi-mcp" or drop the JSON config into Cursor, Windsurf, Claude Desktop, or custom agent runners. Your assistant gains 40 tools covering match schedules, live scores, player stats, and round-by-round replay timelines without writing any scraping code.',
  },
  {
    question: 'Do I need to host an MCP server or manage background processes?',
    answer:
      'No. The MCP server runs on demand over standard stdio using uvx. There are no servers to host, no ports to open, and no API keys required. Your AI client launches the process automatically when a session starts and shuts it down when you finish.',
  },
  {
    question: 'Do I need an API key or account?',
    answer:
      'No. Install the package or run the MCP server and start making calls immediately. There is no key, no signup, no billing, and no environment variable to configure.',
  },
  {
    question: 'Can I export data into Pandas, Polars, or Excel spreadsheets?',
    answer:
      'Yes! Every model in v3.1 inherits from ExportableModel, giving you one-line export methods: .to_df() for pandas, .to_polars() for Polars, .to_csv(), .to_parquet(), .to_excel(), .to_json(), and .to_markdown().',
  },
  {
    question: 'Does it support async Python?',
    answer:
      'The Python client is intentionally synchronous to keep the dependency surface minimal and the call path predictable. In an async app, run calls in a worker thread (asyncio.to_thread) or background task. Scripts, scheduled jobs, and data pipelines can use it directly.',
  },
  {
    question: 'How are rate limits handled?',
    answer:
      'Each client is rate limited to three requests per second by default, configurable with requests_per_second. Requests retry automatically with exponential backoff, so temporary network hiccups do not fail your script.',
  },
  {
    question: 'What data can I actually fetch?',
    answer:
      'Matches (upcoming, live, completed), series (map scores, player stats, economy buy matrices, 2D kill-feed replays, VODs), teams (rosters, staff, match history, placements, transactions), players (career profiles, agent stats, placements), events (stages, brackets, standings), and editorial news with full Markdown.',
  },
  {
    question: 'Which Python versions are supported?',
    answer:
      'Python 3.11 and newer, including 3.12, 3.13, 3.14, and 3.15. The package is MIT licensed, so you can use it in commercial and open-source projects without restriction.',
  },
];

export function Faq() {
  return (
    <div className="grid gap-10 lg:grid-cols-[minmax(0,0.7fr)_minmax(0,1.3fr)] lg:gap-20">
      <div>
        <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">FAQ</p>
        <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl">
          Questions,
          <br />
          <span className="text-fd-muted">answered.</span>
        </h2>
        <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-fd-muted">
          Keys, MCP server, AI integrations, data science exports, coverage, rate limits, and licensing.
        </p>
        <Link
          href="/faq/"
          className="group mt-6 inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
        >
          Read the full FAQ
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      </div>

      <FaqAccordion
        items={faqs.map((faq) => ({ q: faq.question, a: faq.answer }))}
        questionClassName="text-[14.5px] font-medium text-white/80 transition-colors group-hover:text-white"
        answerClassName="max-w-2xl pb-5 pr-8 text-[13.5px] leading-relaxed text-white/50"
      />
    </div>
  );
}
