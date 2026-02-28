import { useQuery } from '@tanstack/react-query'
import { fetchCompetitors } from '../api'
import { useFilterStore } from '../store'
import type { Competitor } from '../types'

const BRAND_STYLES: Record<string, { ring: string; dot: string; badge: string }> = {
  bebodywise: {
    ring: 'ring-pink-200',
    dot: 'bg-pink-400',
    badge: 'bg-pink-50 text-pink-700',
  },
  man_matters: {
    ring: 'ring-blue-200',
    dot: 'bg-blue-400',
    badge: 'bg-blue-50 text-blue-700',
  },
  little_joys: {
    ring: 'ring-emerald-200',
    dot: 'bg-emerald-400',
    badge: 'bg-emerald-50 text-emerald-700',
  },
}

const BRAND_LABELS: Record<string, string> = {
  bebodywise: 'Bebodywise',
  man_matters: 'Man Matters',
  little_joys: 'Little Joys',
}

function CompetitorCard({ c }: { c: Competitor }) {
  const styles = BRAND_STYLES[c.brand] ?? {
    ring: 'ring-slate-200',
    dot: 'bg-slate-400',
    badge: 'bg-slate-50 text-slate-700',
  }

  return (
    <div
      className={`flex-none w-52 rounded-xl border border-slate-100 bg-white p-4 shadow-sm
                  ring-2 ${styles.ring} hover:shadow-md transition-shadow`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <p className="text-sm font-semibold text-slate-800 leading-tight line-clamp-2">
          {c.competitor_name}
        </p>
        <span className={`flex-none rounded-full px-2 py-0.5 text-[10px] font-semibold ${styles.badge}`}>
          {BRAND_LABELS[c.brand] ?? c.brand}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
        <div>
          <p className="text-slate-400 font-medium">Total Ads</p>
          <p className="text-slate-800 font-bold text-base leading-tight">{c.total_ads}</p>
        </div>
        <div>
          <p className="text-slate-400 font-medium">Active</p>
          <p className="text-emerald-600 font-bold text-base leading-tight">{c.active_ads}</p>
        </div>
        <div>
          <p className="text-slate-400 font-medium">Avg Spend</p>
          <p className="text-slate-700 font-semibold">
            ₹{c.avg_spend != null ? Math.round(c.avg_spend).toLocaleString('en-IN') : '—'}
          </p>
        </div>
        <div>
          <p className="text-slate-400 font-medium">Max Days</p>
          <p className={`font-semibold ${c.max_days_running >= 60 ? 'text-orange-500' : 'text-slate-700'}`}>
            {c.max_days_running >= 60 ? '🔥 ' : ''}{c.max_days_running}d
          </p>
        </div>
      </div>

      {/* Top theme */}
      {c.top_theme && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mb-1">
            Top Theme
          </p>
          <span className="inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600 font-medium capitalize">
            {c.top_theme.replace(/_/g, ' ')}
          </span>
        </div>
      )}
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="flex-none w-52 rounded-xl border border-slate-100 bg-white p-4 shadow-sm animate-pulse">
      <div className="h-4 bg-slate-200 rounded w-3/4 mb-3" />
      <div className="grid grid-cols-2 gap-2">
        <div className="h-8 bg-slate-100 rounded" />
        <div className="h-8 bg-slate-100 rounded" />
        <div className="h-8 bg-slate-100 rounded" />
        <div className="h-8 bg-slate-100 rounded" />
      </div>
    </div>
  )
}

export function CompetitorSummaryBar() {
  const brand = useFilterStore((s) => s.brand)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['competitors', brand],
    queryFn: () => fetchCompetitors(brand || undefined),
  })

  return (
    <div className="bg-slate-50 border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Competitors
            {data && (
              <span className="ml-2 text-slate-400 font-normal normal-case">
                — {data.count} tracked
              </span>
            )}
          </h2>
        </div>

        {isError && (
          <p className="text-sm text-red-500 py-2">
            Could not load competitors. Is the backend running at localhost:8000?
          </p>
        )}

        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
          {isLoading
            ? Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
            : data?.data.map((c) => <CompetitorCard key={c.competitor_name} c={c} />)}
        </div>
      </div>
    </div>
  )
}
