import Link from 'next/link';
import { ArrowUpRight, Bot, Cpu, Sparkles, Terminal, Zap } from 'lucide-react';
import { CopyButton } from '@/components/landing/copy-button';
import { Reveal } from '@/components/landing/reveal';
import { SpotlightCard } from '@/components/landing/spotlight-card';
import { project } from '@/lib/project';

const clients = [
  'Claude Desktop',
  'Cursor',
  'Claude Code',
  'Windsurf',
  'OpenCode',
  'DeepSeek',
  'Codex',
  'Grok',
  'Zed',
];

const examplePrompts = [
  {
    prompt: 'Who is playing live right now in VCT?',
    tool: 'matches_live()',
    desc: 'Live scoreboard & active maps',
  },
  {
    prompt: 'Compare Sentinels vs FNATIC head-to-head',
    tool: 'compare_teams(team1, team2)',
    desc: 'Rosters, form, rankings & earnings',
  },
  {
    prompt: "Give me Derke's career summary and top agents",
    tool: 'get_player_career_summary(id)',
    desc: 'ACS, K/D, rating & tournament placements',
  },
  {
    prompt: 'What was the round-by-round economy in the Grand Final?',
    tool: 'series_economy(series_id)',
    desc: 'Buy matrices, loadouts, credits & bank',
  },
];

const claudeCodeCmd = 'claude mcp add vlrdevapi -- uvx --from "vlrdevapi[mcp]" vlrdevapi-mcp';

const dropInJson = `{
  "mcpServers": {
    "vlrdevapi": {
      "command": "uvx",
      "args": ["--from", "vlrdevapi[mcp]", "vlrdevapi-mcp"]
    }
  }
}`;

/**
 * Model Context Protocol (MCP) showcase section on the homepage.
 * Sits directly between 'What it handles' (Features) and 'The namespaces' (ModuleShowcase).
 */
export function McpSection() {
  return (
    <section className="relative border-b border-white/10 bg-fd-canvas">
      {/* Subtle glow effect */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(255,70,85,0.08),transparent_70%)]"
      />

      <div className="relative mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
        <Reveal className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-[12px] text-fd-primary">
              <Bot className="size-3.5" aria-hidden="true" />
              <span>Model Context Protocol · v{project.version}</span>
            </div>
            <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl lg:text-[2.9rem]">
              Connect any AI assistant
              <br />
              <span className="text-fd-muted">to live Valorant esports.</span>
            </h2>
          </div>
          <div className="max-w-md lg:text-right">
            <p className="text-[14.5px] leading-relaxed text-fd-subtle">
              No API keys. No hosting. No custom glue code. Run with <code className="font-mono text-white/80">uvx</code> in
              ten seconds with drop-in support for any MCP-compatible client.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 lg:justify-end">
              <Link
                href="/docs/mcp/"
                className="group inline-flex items-center gap-1.5 border border-white bg-white px-4 py-2 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
              >
                10-second setup guide
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <Link
                href="/docs/reference/mcp/"
                className="inline-flex items-center gap-1.5 border border-white/15 px-4 py-2 text-[13px] font-medium text-white/80 transition-colors hover:border-white/30 hover:bg-white/[0.04] hover:text-white"
              >
                All 40 tools
              </Link>
            </div>
          </div>
        </Reveal>

        {/* Supported client pills */}
        <Reveal delay={60} className="mt-10 flex flex-wrap items-center gap-2 border-y border-white/10 py-4">
          <span className="mr-2 font-mono text-[11px] uppercase tracking-[0.16em] text-fd-muted">
            Drop-in ready:
          </span>
          {clients.map((client) => (
            <span
              key={client}
              className="border border-white/[0.08] bg-white/[0.02] px-2.5 py-1 font-mono text-[12px] text-white/70"
            >
              {client}
            </span>
          ))}
        </Reveal>

        {/* Dual Bento Grid */}
        <div className="mt-8 grid gap-4 lg:grid-cols-12">
          {/* Quick Copy / Setup Card */}
          <Reveal delay={100} className="lg:col-span-6">
            <SpotlightCard className="flex h-full flex-col p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Quickest Setup
                  </p>
                  <h3 className="mt-2 text-lg font-medium tracking-tight text-white sm:text-xl">
                    One terminal command or drop-in JSON
                  </h3>
                </div>
                <Terminal className="size-5 shrink-0 text-fd-primary" aria-hidden="true" />
              </div>

              {/* Claude Code CLI */}
              <div className="mt-6 border border-white/10 bg-black/60 p-3.5">
                <div className="flex items-center justify-between text-[12px] text-fd-muted">
                  <span className="font-mono">Claude Code CLI</span>
                  <CopyButton value={claudeCodeCmd} label="Copy command" />
                </div>
                <pre className="mt-2 overflow-x-auto font-mono text-[12.5px] text-white/90">
                  <code>{claudeCodeCmd}</code>
                </pre>
              </div>

              {/* Drop-in JSON for Cursor / Claude Desktop / Windsurf */}
              <div className="mt-3 flex-1 border border-white/10 bg-black/60 p-3.5">
                <div className="flex items-center justify-between text-[12px] text-fd-muted">
                  <span className="font-mono">Cursor / Claude Desktop / Windsurf config</span>
                  <CopyButton value={dropInJson} label="Copy JSON" />
                </div>
                <pre className="mt-2 overflow-x-auto font-mono text-[12px] text-fd-subtle">
                  <code>{dropInJson}</code>
                </pre>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3 text-[12px] text-fd-muted">
                <span>Runs isolated via uvx</span>
                <span className="font-mono text-white/60">No venv activation required</span>
              </div>
            </SpotlightCard>
          </Reveal>

          {/* Natural Language Prompt & Tool Matching Card */}
          <Reveal delay={140} className="lg:col-span-6">
            <SpotlightCard className="flex h-full flex-col p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    What Agents Can Query
                  </p>
                  <h3 className="mt-2 text-lg font-medium tracking-tight text-white sm:text-xl">
                    40 tools &amp; composite dossiers
                  </h3>
                </div>
                <Sparkles className="size-5 shrink-0 text-fd-primary" aria-hidden="true" />
              </div>

              <div className="mt-6 space-y-2.5">
                {examplePrompts.map((item) => (
                  <div
                    key={item.prompt}
                    className="border border-white/[0.08] bg-white/[0.02] p-3 transition-colors hover:border-white/20"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-[13px] font-medium text-white/90">&ldquo;{item.prompt}&rdquo;</p>
                      <span className="shrink-0 font-mono text-[11px] text-fd-primary">{item.tool}</span>
                    </div>
                    <p className="mt-1 text-[12px] text-fd-muted">{item.desc}</p>
                  </div>
                ))}
              </div>

              <div className="mt-auto border-t border-white/10 pt-4">
                <div className="flex items-center justify-between text-[12.5px]">
                  <span className="text-fd-muted">Autonomous agents prompt</span>
                  <Link
                    href="/docs/mcp/#autonomous-ai-agents-opencode-deepseek-codex-grok-etc"
                    className="group inline-flex items-center gap-1 font-mono text-fd-primary transition-colors hover:underline"
                  >
                    View agent prompt
                    <ArrowUpRight className="size-3" aria-hidden="true" />
                  </Link>
                </div>
              </div>
            </SpotlightCard>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
