import type { ReactNode } from 'react';

interface OGTemplateProps {
  title: ReactNode;
  description?: ReactNode;
  site?: ReactNode;
}

const ACCENT = '#ff4655';
const BG_DARK = '#0d1117';
const BG_LIGHT = '#161b22';
const TEXT_MUTED = '#8b949e';
const TEXT_WHITE = '#ffffff';

export function OGTemplate({ title, description, site = 'VLRdevAPI' }: OGTemplateProps) {
  return (
    <div
      style={{
        display: 'flex',
        width: '100%',
        height: '100%',
        background: `linear-gradient(135deg, ${BG_DARK} 0%, ${BG_LIGHT} 100%)`,
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
          height: '100%',
          padding: '56px 64px',
          position: 'relative',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: '14px',
            }}
          >
            <svg width="40" height="40" viewBox="0 0 2000 2000" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M138.446,138.446l1723.108,617.857l0,258.466l-625.747,223.481l96.545,-269.249l243.659,-84.696l-1336.257,-462.198l-101.308,-283.661Zm829.612,1195.429l-829.612,296.29l101.308,-281.373l821.972,-285.72l-93.668,270.803Z" fill="#ffffff"/>
              <path d="M534.163,1246.454l-294.41,-824.347l276.723,95.716l227.877,655.568l-210.191,73.063Zm710.217,-711.452l93.137,-269.267l292.648,-127.289l-169.945,473.95l-215.84,-77.394Zm-360.075,1041.008l287.601,-831.48l214.349,74.141l-373.948,1042.882l-258.466,0l-142.905,-400.135l207.746,-74.195l65.623,188.787Z" fill={ACCENT}/>
            </svg>
            <span
              style={{
                fontSize: '28px',
                fontWeight: 700,
                color: ACCENT,
                letterSpacing: '0.1em',
              }}
            >
              {site}
            </span>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            flex: 1,
            flexDirection: 'column',
            justifyContent: 'center',
            marginTop: '-20px',
          }}
        >
          <div
            style={{
              width: '80px',
              height: '4px',
              backgroundColor: ACCENT,
              borderRadius: '2px',
              marginBottom: '24px',
            }}
          />

          <h1
            style={{
              fontSize: '64px',
              fontWeight: 800,
              color: TEXT_WHITE,
              margin: 0,
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
              maxWidth: '900px',
            }}
          >
            {title}
          </h1>

          {description && (
            <p
              style={{
                fontSize: '28px',
                fontWeight: 400,
                color: TEXT_MUTED,
                margin: 0,
                marginTop: '16px',
                lineHeight: 1.4,
                maxWidth: '850px',
              }}
            >
              {description}
            </p>
          )}
        </div>

        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '24px',
            borderTop: `1px solid rgba(255,255,255,0.08)`,
          }}
        >
          <span
            style={{
              fontSize: '20px',
              color: TEXT_MUTED,
              fontWeight: 400,
            }}
          >
            vlrdevapi.pages.dev
          </span>

          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <div
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: ACCENT,
              }}
            />
            <span
              style={{
                fontSize: '20px',
                color: TEXT_MUTED,
                fontWeight: 500,
              }}
            >
              RiftWatch
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
