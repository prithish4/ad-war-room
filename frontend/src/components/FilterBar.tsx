import { useFilterStore } from '../store'
import type { BrandFilter, DateRangeFilter, FormatFilter } from '../types'

const BRANDS: { value: BrandFilter; label: string }[] = [
  { value: '', label: 'All Brands' },
  { value: 'bebodywise', label: 'Bebodywise' },
  { value: 'man_matters', label: 'Man Matters' },
  { value: 'little_joys', label: 'Little Joys' },
]

const FORMATS: { value: FormatFilter; label: string }[] = [
  { value: '', label: 'All Formats' },
  { value: 'static', label: '🖼 Static' },
  { value: 'video', label: '🎬 Video' },
  { value: 'carousel', label: '🎠 Carousel' },
]

const DATE_RANGES: { value: DateRangeFilter; label: string }[] = [
  { value: 'all', label: 'All Time' },
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '60', label: 'Last 60 days' },
]

export function FilterBar({ totalShown, totalAll }: { totalShown: number; totalAll: number }) {
  const { brand, format, dateRange, setBrand, setFormat, setDateRange, resetFilters } =
    useFilterStore()

  const isFiltered = brand !== '' || format !== '' || dateRange !== 'all'

  return (
    <div className="sticky top-0 z-10 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1">
          Filters
        </span>

        {/* Brand */}
        <select
          value={brand}
          onChange={(e) => setBrand(e.target.value as BrandFilter)}
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {BRANDS.map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>

        {/* Format */}
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as FormatFilter)}
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {FORMATS.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>

        {/* Date range */}
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value as DateRangeFilter)}
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {DATE_RANGES.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>

        {/* Reset */}
        {isFiltered && (
          <button
            onClick={resetFilters}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium underline
                       underline-offset-2 transition-colors"
          >
            Clear filters
          </button>
        )}

        {/* Count */}
        <span className="ml-auto text-sm text-slate-500">
          Showing{' '}
          <span className="font-semibold text-slate-800">{totalShown}</span>
          {totalShown !== totalAll && (
            <> of <span className="font-semibold text-slate-800">{totalAll}</span></>
          )}{' '}
          ads
        </span>
      </div>
    </div>
  )
}
