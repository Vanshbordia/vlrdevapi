import { CopyButton } from './copy-button';

export function CopyCommand({
  command,
  className = '',
}: {
  command: string;
  className?: string;
}) {
  return (
    <div
      className={`inline-flex h-11 max-w-full items-center gap-2 border border-white/15 bg-white/[0.03] pl-4 pr-1.5 transition-colors hover:border-white/25 hover:bg-white/[0.06] ${className}`}
    >
      <span aria-hidden="true" className="font-mono text-xs text-[#ff4655]">
        $
      </span>
      <code className="truncate font-mono text-[13px] text-white/80">{command}</code>
      <CopyButton
        value={command}
        label={`Copy command: ${command}`}
        className="border-0 bg-transparent"
      />
    </div>
  );
}
