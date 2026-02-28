import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { fetchAds } from '../api'
import { useFilterStore } from '../store'
import type { Ad } from '../types'
import { AdCard } from './AdCard'

function filterByDateRange(ads: Ad[], range: string): Ad[] {
  if (range === 'all') return ads
  const daysAgo = parseInt(range, 10)
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - daysAgo)
  const cutoffStr = cutoff.toISOString().split('T')[0]
  return ads.filter((ad) => ad.start_date >= cutoffStr)
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-slate-200 border-l-4 border-l-slate-300 bg-white shadow-sm animate-pulse">
      <div className="px-4 pt-4 pb-3 border-b border-slate-100">
        <div className="h-4 bg-slate-200 rounded w-2/3 mb-2" />
        <div className="flex gap-2">
          <div className="h-3 bg-slate-100 rounded w-12" />
          <div className="h-3 bg-slate-100 rounded w-16" />
          <div className="h-3 bg-slate-100 rounded w-10" />
        </div>
      </div>
      <div className="px-4 py-3">
        <div className="h-4 bg-slate-200 rounded w-full mb-2" />
        <div className="h-3 bg-slate-100 rounded w-full mb-1" />
        <div className="h-3 bg-slate-100 rounded w-4/5 mb-1" />
        <div className="h-3 bg-slate-100 rounded w-3/5" />
      </div>
      <div className="px-4 pb-4 pt-2 border-t border-slate-100 flex justify-between">
        <div className="h-3 bg-slate-100 rounded w-20" />
        <div className="h-3 bg-slate-100 rounded w-24" />
      </div>
    </div>
  )
}

interface AdGridProps {
  onCountsReady: (shown: number, total: number) => void
}

export function AdGrid({ onCountsReady }: AdGridProps) {
  const { brand, format, dateRange } = useFilterStore()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['ads', brand, format],
    queryFn: () => fetchAds({ brand: brand || undefined, ad_format: format || undefined }),
    staleTime: 30_000,
  })

  const filtered = useMemo(() => {
    if (!data) return []
    return filterByDateRange(data.data, dateRange)
  }, [data, dateRange])

  // Bubble counts up to parent for the filter bar label
  useMemo(() => {
    onCountsReady(filtered.length, data?.total ?? 0)
  }, [filtered.length, data?.total, onCountsReady])

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center px-4">
        <span className="text-4xl mb-4">⚠️</span>
        <p className="text-slate-700 font-semibold mb-1">Could not reach the backend</p>
        <p className="text-sm text-slate-500">
          Make sure FastAPI is running at{' '}
          <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">localhost:8000</code>{' '}
          and the database has been seeded.
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  if (filtered.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <span className="text-4xl mb-4">🔍</span>
        <p className="text-slate-700 font-semibold mb-1">No ads match your filters</p>
        <p className="text-sm text-slate-500">Try widening the date range or clearing filters.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {filtered.map((ad) => (
        <AdCard key={ad.id} ad={ad} />
      ))}
    </div>
  )
}
