import type { ReactNode } from 'react';
import { siteUrl } from '@/lib/shared';

interface OGTemplateProps {
  title: ReactNode;
  description?: ReactNode;
  /** Small uppercase label above the headline, e.g. `Blog`. */
  eyebrow?: ReactNode;
  /** Text shown at the bottom right, e.g. `pip install vlrdevapi`. */
  command?: ReactNode;
  /** Origin shown in the footer. Defaults to the configured site origin. */
  origin?: string;
}

/**
 * Social card template.
 *
 * Mirrors the marketing site: near-black surfaces, the `#ff4655` accent,
 * hairline borders, an uppercase tracked label and a tight display headline.
 * The typeface is Geist, which `next/og` bundles, so the card matches the
 * site without shipping an extra font file.
 */
const ACCENT = '#ff4655';
const ACCENT_SOFT = '#ff8d97';
const BG = '#000000';
const BG_RAISED = '#0a0a0a';
const TEXT = '#ffffff';
const TEXT_SUBTLE = '#a1a1aa';
const TEXT_MUTED = '#8a8a93';
const HAIRLINE = 'rgba(255,255,255,0.12)';

/** The VLRdevAPI mark. */
function Mark({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 2000 2000" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M138.446,138.446l1723.108,617.857l0,258.466l-625.747,223.481l96.545,-269.249l243.659,-84.696l-1336.257,-462.198l-101.308,-283.661Zm829.612,1195.429l-829.612,296.29l101.308,-281.373l821.972,-285.72l-93.668,270.803Z"
        fill={TEXT}
      />
      <path
        d="M534.163,1246.454l-294.41,-824.347l276.723,95.716l227.877,655.568l-210.191,73.063Zm710.217,-711.452l93.137,-269.267l292.648,-127.289l-169.945,473.95l-215.84,-77.394Zm-360.075,1041.008l287.601,-831.48l214.349,74.141l-373.948,1042.882l-258.466,0l-142.905,-400.135l207.746,-74.195l65.623,188.787Z"
        fill={ACCENT}
      />
    </svg>
  );
}

/**
 * The tactical corner ticks from the hero demo, drawn as one inline SVG so
 * the coordinates are exact.
 *
 * Satori supports inline `<svg>` elements and `position: absolute` with
 * `top`/`left`, so the layer is pinned to the card's top-left corner.
 */
function CornerTicks() {
  return (
    <svg
      width={1200}
      height={630}
      viewBox="0 0 1200 630"
      style={{ position: 'absolute', top: 0, left: 0 }}
    >
      <path d="M22 54 V22 H54" stroke={ACCENT} strokeWidth={3} fill="none" />
      <path d="M1146 22 H1178 V54" stroke="rgba(255,255,255,0.30)" strokeWidth={3} fill="none" />
      <path d="M22 576 V608 H54" stroke="rgba(255,255,255,0.30)" strokeWidth={3} fill="none" />
      <path d="M1146 608 H1178 V576" stroke={ACCENT} strokeWidth={3} fill="none" />
    </svg>
  );
}

export function OGTemplate({
  title,
  description,
  eyebrow,
  command = 'pip install vlrdevapi',
  origin = siteUrl,
}: OGTemplateProps) {
  const host = origin.replace(/^https?:\/\//, '').replace(/\/+$/, '');

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        padding: '64px 72px',
        backgroundColor: BG,
        backgroundImage: `radial-gradient(900px circle at 88% -10%, rgba(255,70,85,0.18), transparent 60%), linear-gradient(160deg, ${BG_RAISED} 0%, ${BG} 55%)`,
        color: TEXT,
        fontFamily: 'Geist',
        position: 'relative',
      }}
    >
      <CornerTicks />

      {/* Header: mark + wordmark */}
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '14px' }}>
        <Mark />
        <span
          style={{
            display: 'flex',
            flexDirection: 'row',
            fontSize: '26px',
            fontWeight: 700,
            letterSpacing: '0.01em',
            
          }}
        >
          <span style={{ color: TEXT }}>VLR</span>
          <span style={{ color: TEXT_MUTED }}>dev</span>
          <span style={{ color: TEXT }}>API</span>
        </span>
        {eyebrow ? (
          <span
            style={{
              marginLeft: '6px',
              padding: '6px 14px',
              border: `1px solid ${HAIRLINE}`,
              color: TEXT_MUTED,
              fontSize: '18px',
              fontWeight: 500,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
            }}
          >
            {eyebrow}
          </span>
        ) : null}
      </div>

      {/* Body */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          flex: 1,
          justifyContent: 'center',
          paddingTop: '10px',
        }}
      >
        <div
          style={{
            width: '84px',
            height: '5px',
            backgroundColor: ACCENT,
            marginBottom: '24px',
          }}
        />

        <div
          style={{
            display: 'flex',
            fontSize: '60px',
            fontWeight: 800,
            lineHeight: 1.08,
            letterSpacing: '-0.03em',
            maxWidth: '980px',
          }}
        >
          {title}
        </div>

        {description ? (
          <div
            style={{
              display: 'flex',
              marginTop: '20px',
              fontSize: '25px',
              fontWeight: 400,
              lineHeight: 1.45,
              color: TEXT_SUBTLE,
              maxWidth: '880px',
            }}
          >
            {description}
          </div>
        ) : null}
      </div>

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: '22px',
          borderTop: `1px solid ${HAIRLINE}`,
        }}
      >
        <div style={{ display: 'flex', fontSize: '19px', color: TEXT_MUTED }}>{host}</div>

        <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '8px 16px',
              border: `1px solid ${HAIRLINE}`,
              backgroundColor: 'rgba(255,255,255,0.03)',
              fontSize: '19px',
              fontWeight: 500,
              color: ACCENT_SOFT,
            }}
          >
            <div
              style={{
                display: 'flex',
                width: '9px',
                height: '9px',
                borderRadius: '50%',
                backgroundColor: ACCENT,
              }}
            />
            {command}
          </div>
        </div>
      </div>
    </div>
  );
}
