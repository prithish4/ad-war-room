import { useCallback, useState } from 'react'
import { AdGrid } from './components/AdGrid'
import { CompetitorSummaryBar } from './components/CompetitorSummaryBar'
import { FilterBar } from './components/FilterBar'
import { WeeklyBrief } from './components/WeeklyBrief'

export default function App() {
  const [shownCount, setShownCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)

  const handleCounts = useCallback((shown: number, total: number) => {
    setShownCount(shown)
    setTotalCount(total)
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* ── Header ── */}
      <header className="bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-5 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              Ad Intelligence
              <span className="ml-2 text-slate-400 font-normal text-base">War Room</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Competitive ad tracking for Bebodywise · Man Matters · Little Joys
            </p>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xs text-slate-400">Powered by</span>
            <span className="rounded-full bg-indigo-600 px-3 py-1 text-xs font-semibold text-white">
              Claude AI
            </span>
          </div>
        </div>
      </header>

      {/* ── Competitor summary strip ── */}
      <CompetitorSummaryBar />

      {/* ── Sticky filter bar ── */}
      <FilterBar totalShown={shownCount} totalAll={totalCount} />

      {/* ── Two-column content ── */}
      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6 items-start">

        {/* Left — ad grid (fills remaining width) */}
        <main className="flex-1 min-w-0">
          <AdGrid onCountsReady={handleCounts} />
        </main>

        {/* Right — weekly brief panel (sticky, desktop only) */}
        <aside className="hidden lg:block w-80 flex-none">
          {/* top-[54px] keeps the panel below the sticky FilterBar (~54 px tall) */}
          <div className="sticky top-[54px] max-h-[calc(100vh-70px)] overflow-y-auto rounded-xl">
            <WeeklyBrief />
          </div>
        </aside>
      </div>
    </div>
  )
}
