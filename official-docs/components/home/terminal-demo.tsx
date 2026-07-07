'use client';

import { Terminal } from '@/components/ui/terminal';

export function TerminalDemo() {
  return (
    <Terminal
      commands={[
        'pip install vlrdevapi',
        'python',
        '>>> import vlrdevapi',
        '>>> matches = vlrdevapi.matches.upcoming()',
        '>>> for m in matches.matches[:5]:',
        '...     print(f"    {m.team1.name:20s} vs {m.team2.name:20s}")',
      ]}
      outputs={{
        0: ['Successfully installed vlrdevapi-2.0.0'],
        1: ['Python 3.12.0 (main, Oct 2 2024)'],
        5: [
          'Sentinels           vs NRG',
          'FNATIC              vs Cloud9',
          'LOUD                vs DRX',
          'Team Heretics       vs Zeta Division',
          'Evil Geniuses       vs 100 Thieves',
        ],
      }}
      typingSpeed={45}
      delayBetweenCommands={1000}
    />
  );
}
