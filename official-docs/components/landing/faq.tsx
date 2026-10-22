import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { FaqAccordion } from '@/components/marketing/faq-accordion';

const faqs = [
  {
    question: 'Is VLRdevAPI an official VLR.gg API?',
    answer:
      'No. VLRdevAPI is an independent, open-source Python client that reads publicly available pages on VLR.gg and converts them into typed models. It is not affiliated with, endorsed by, or supported by VLR.gg or Riot Games.',
  },
  {
    question: 'Do I need an API key or account?',
    answer:
      'No. Install the package and start making calls. There is no key, no signup, no billing, and no environment variable to configure before your first request.',
  },
  {
    question: 'Does it support async Python?',
    answer:
      'The client is intentionally synchronous to keep the dependency surface small and the call path predictable. In an async app, run calls in a worker thread or background task. Scripts, scheduled jobs, and data pipelines can use it directly.',
  },
  {
    question: 'How are rate limits handled?',
    answer:
      'Each client is rate limited to three requests per second by default, and you can change that with requests_per_second. Requests also retry automatically with exponential backoff, so temporary failures do not take down a job.',
  },
  {
    question: 'What data can I actually fetch?',
    answer:
      'Players, teams, matches, series, events, and news. That includes profiles and career history, rosters and placements, live and completed matches, map and round data, economy breakdowns, tournament stages and standings, plus full articles as Markdown.',
  },
  {
    question: 'Which Python versions are supported?',
    answer:
      'Python 3.11 and newer, including 3.12 through 3.14. The package is MIT licensed, so you can use it in commercial and open-source projects.',
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
          Keys, coverage, rate limits, and licensing. The full FAQ goes deeper on each of them.
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
