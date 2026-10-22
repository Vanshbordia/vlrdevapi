import { ChevronDown } from 'lucide-react';
import type { ReactNode } from 'react';

export interface FaqAccordionItem {
  /** The question. Used as the React key. */
  q: string;
  /** The answer. May contain links and inline code. */
  a: ReactNode;
}

/**
 * Native `<details>` disclosure list.
 *
 * The native marker is hidden only in engines that support
 * `::-webkit-details-marker`, so Firefox keeps its disclosure triangle.
 * See `.faq-summary` in `app/global.css`.
 */
export function FaqAccordion({
  items,
  questionClassName = 'text-[14.5px] font-medium text-white/80 transition-colors group-hover:text-white',
  answerClassName = 'max-w-2xl pb-5 pr-10 text-[13.5px] leading-relaxed text-white/50',
}: {
  items: FaqAccordionItem[];
  questionClassName?: string;
  answerClassName?: string;
}) {
  return (
    <div className="border-t border-white/10">
      {items.map((item) => (
        <details key={item.q} className="group border-b border-white/10">
          <summary className="faq-summary flex cursor-pointer items-start justify-between gap-6 py-5">
            <span className={questionClassName}>{item.q}</span>
            <span
              aria-hidden="true"
              className="mt-0.5 flex size-7 shrink-0 items-center justify-center border border-white/10 text-fd-muted transition-colors group-open:border-fd-primary/40 group-open:bg-fd-primary/10 group-open:text-fd-primary"
            >
              <ChevronDown className="size-3.5 transition-transform duration-200 group-open:rotate-180" />
            </span>
          </summary>
          <div className={answerClassName}>{item.a}</div>
        </details>
      ))}
    </div>
  );
}
