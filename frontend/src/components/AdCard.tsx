import type { Ad } from '../types'

const BRAND_STYLES: Record<string, { pill: string; border: string }> = {
  bebodywise:  { pill: 'bg-pink-100 text-pink-700',    border: 'border-l-pink-400' },
  man_matters: { pill: 'bg-blue-100 text-blue-700',    border: 'border-l-blue-400' },
  little_joys: { pill: 'bg-emerald-100 text-emerald-700', border: 'border-l-emerald-400' },
}

const THEME_PILL: Record<string, string> = {
  hair_loss:   'bg-orange-100 text-orange-700',
  energy:      'bg-yellow-100 text-yellow-700',
  immunity:    'bg-green-100 text-green-700',
  weight:      'bg-purple-100 text-purple-700',
  performance: 'bg-blue-100 text-blue-700',
  confidence:  'bg-pink-100 text-pink-700',
  parenting:   'bg-teal-100 text-teal-700',
  safety:      'bg-red-100 text-red-700',
}

const FORMAT_ICON: Record<string, string> = {
  static:   '🖼',
  video:    '🎬',
  carousel: '🎠',
}

const BRAND_LABELS: Record<string, string> = {
  bebodywise:  'Bebodywise',
  man_matters: 'Man Matters',
  little_joys: 'Little Joys',
}

function formatSpend(min: number, max: number) {
  const fmt = (n: number) =>
    n >= 1_00_000
      ? `₹${(n / 1_00_000).toFixed(1)}L`
      : n >= 1_000
      ? `₹${(n / 1_000).toFixed(0)}K`
      : `₹${n}`
  return `${fmt(min)} – ${fmt(max)}`
}

export function AdCard({ ad }: { ad: Ad }) {
  const brandStyle = BRAND_STYLES[ad.brand] ?? { pill: 'bg-slate-100 text-slate-700', border: 'border-l-slate-400' }
  const themePill  = THEME_PILL[ad.message_theme] ?? 'bg-slate-100 text-slate-600'
  const isLongRunning = ad.days_running >= 60

  return (
    <div
      className={`flex flex-col bg-white rounded-xl border border-slate-200 border-l-4
                  ${brandStyle.border} shadow-sm hover:shadow-md transition-shadow duration-200`}
    >
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-slate-100">
        <div className="flex items-start justify-between gap-2 mb-2">
          <p className="text-sm font-bold text-slate-800 leading-tight">
            {ad.competitor_name}
          </p>
          <span
            className={`flex-none text-[10px] font-semibold rounded-full px-2 py-0.5 ${brandStyle.pill}`}
          >
            {BRAND_LABELS[ad.brand] ?? ad.brand}
          </span>
        </div>

        {/* Badges row */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-slate-500 font-medium">
            {FORMAT_ICON[ad.ad_format] ?? '📄'} {ad.ad_format}
          </span>
          <span className="text-slate-300">·</span>
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${themePill}`}
          >
            {ad.message_theme.replace(/_/g, ' ')}
          </span>
          <span className="text-slate-300">·</span>
          <span
            className={`text-xs font-semibold ${isLongRunning ? 'text-orange-500' : 'text-slate-500'}`}
            title={`Running since ${ad.start_date}`}
          >
            {isLongRunning ? '🔥 ' : ''}
            {ad.days_running}d
          </span>
          {!ad.is_active && (
            <>
              <span className="text-slate-300">·</span>
              <span className="text-[10px] text-slate-400 font-medium italic">stopped</span>
            </>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-3 flex-1">
        <p className="text-sm font-semibold text-slate-800 mb-1 line-clamp-2 leading-snug">
          {ad.headline}
        </p>
        <p className="text-xs text-slate-500 line-clamp-3 leading-relaxed">
          {ad.body_text}
        </p>
      </div>

      {/* Footer */}
      <div className="px-4 pb-4 pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
        <span className="text-[10px] text-slate-400 font-medium truncate">
          {ad.platform.replace(',', ' + ')}
        </span>

        <div className="flex items-center gap-2 flex-none">
          <span className="text-[10px] text-slate-500 font-medium">
            {formatSpend(ad.estimated_spend_min, ad.estimated_spend_max)}
            <span className="text-slate-400">/day</span>
          </span>
          <span className="rounded bg-indigo-50 text-indigo-600 px-2 py-0.5 text-[10px] font-semibold">
            {ad.cta}
          </span>
        </div>
      </div>
    </div>
  )
}
