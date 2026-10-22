import { Check } from 'lucide-react';
import snapshot from './landing-snapshot.json';

const modelFields = [
  { name: 'player_id', type: 'int', value: String(snapshot.player.id) },
  { name: 'name', type: 'str', value: `"${snapshot.player.name}"` },
  { name: 'real_name', type: 'str', value: `"${snapshot.player.realName}"` },
  { name: 'country', type: 'str', value: `"${snapshot.player.country}"` },
  { name: 'total_winnings', type: 'int', value: String(snapshot.player.totalWinnings) },
];

export function TypedFieldsDemo() {
  return (
    <div className="mt-6 overflow-hidden border border-white/10 bg-fd-canvas">
      <div className="flex items-center justify-between border-b border-white/10 px-3.5 py-2">
        <span className="font-mono text-[12px] text-fd-muted">models.py</span>
        <span className="font-mono text-[12px] uppercase tracking-[0.12em] text-fd-muted">
          runtime validation
        </span>
      </div>

      <div className="p-4 font-mono text-[12px]">
        <p className="text-fd-muted">
          class <span className="text-white/75">PlayerInfo</span>(BaseModel):
        </p>
        <div className="mt-2 space-y-0.5">
          {modelFields.map((field, index) => (
            <div
              key={field.name}
              className="landing-field-focus flex items-center justify-between gap-3 px-2 py-1"
              style={{ animationDelay: `${index * 0.55}s` }}
            >
              <span className="min-w-0 truncate">
                <span className="text-white/75">{field.name}</span>
                <span className="text-fd-muted">: </span>
                <span className="text-fd-primary">{field.type}</span>
              </span>
              <span className="flex shrink-0 items-center gap-2">
                <span className="hidden text-[12px] text-fd-muted sm:inline">{field.value}</span>
                <Check
                  aria-hidden="true"
                  className="landing-check-pop size-3 text-emerald-400/70"
                  style={{ animationDelay: `${index * 0.55}s` }}
                />
              </span>
            </div>
          ))}
        </div>
        <p className="mt-3 text-[12px] text-fd-muted">
          # {snapshot.player.fieldCount} fields · 0 validation errors
        </p>
      </div>
    </div>
  );
}

export function ParallelDemo() {
  return (
    <div className="mt-6 border border-white/10 bg-fd-canvas p-3.5">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[12px] text-fd-muted">event.stages()</span>
        <span className="font-mono text-[12px] uppercase tracking-[0.1em] text-fd-muted">
          thread pool
        </span>
      </div>

      <div className="mt-3 space-y-2">
        {['stage 1', 'stage 2', 'stage 3'].map((lane) => (
          <div key={lane} className="flex items-center gap-2.5">
            <span className="w-12 shrink-0 font-mono text-[12px] text-fd-muted">{lane}</span>
            <div className="relative h-4 flex-1 overflow-hidden bg-white/[0.04]">
              <span className="landing-lane-fill block h-full w-full bg-gradient-to-r from-fd-primary/55 to-fd-primary/15" />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-2 flex justify-between font-mono text-[12px] text-fd-muted">
        <span>dispatched together</span>
        <span>joined once</span>
      </div>
    </div>
  );
}

const seriesDate = new Date(snapshot.series.datetime);
const formatTime = (timeZone: string) =>
  new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone,
  }).format(seriesDate);

const sourceTime = formatTime('America/New_York');
const utcTime = formatTime('UTC');

export function TimezoneDemo() {
  return (
    <div className="mt-6 border border-white/10 bg-fd-canvas p-3.5">
      <div className="flex items-center justify-between gap-3">
        <span className="font-mono text-[12px] text-fd-muted">SeriesInfo.datetime</span>
        <span className="truncate font-mono text-[12px] text-fd-muted">America/New_York</span>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <div className="shrink-0">
          <p className="font-mono text-[12px] uppercase tracking-[0.1em] text-fd-muted">
            VLR.gg
          </p>
          <p className="mt-0.5 font-mono text-lg text-white/75">
            {sourceTime} <span className="text-[12px] text-fd-muted">EDT</span>
          </p>
        </div>

        <div className="relative h-8 min-w-10 flex-1">
          <span aria-hidden="true" className="absolute inset-x-0 top-1/2 h-px bg-white/10" />
          <span aria-hidden="true" className="absolute left-0 top-1/2 size-1 -translate-y-1/2 bg-white/35" />
          <span aria-hidden="true" className="absolute right-0 top-1/2 size-1 -translate-y-1/2 bg-fd-primary" />
          <span
            aria-hidden="true"
            className="landing-tz-dot absolute top-1/2 size-1.5 -translate-y-1/2 bg-fd-primary"
          />
        </div>

        <div className="shrink-0 text-right">
          <p className="font-mono text-[12px] uppercase tracking-[0.1em] text-fd-muted">
            model
          </p>
          <p className="mt-0.5 font-mono text-lg text-fd-primary">
            {utcTime} <span className="text-[12px] text-fd-primary/50">UTC</span>
          </p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-white/10 pt-2 font-mono text-[12px] text-fd-muted">
        <span>source_tz → UTC</span>
        <span className="flex items-center gap-1.5 text-emerald-400/60">
          <span aria-hidden="true" className="size-1 bg-emerald-400/70" />
          tz-aware
        </span>
      </div>
    </div>
  );
}
