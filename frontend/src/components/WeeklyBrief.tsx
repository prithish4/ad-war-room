import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { API_BASE } from '../api'
import { SimpleMarkdown } from './SimpleMarkdown'

const BRANDS: { key: string; label: string; color: string; activeColor: string }[] = [
  {
    key: 'bebodywise',
    label: 'Bebodywise',
    color: 'border-slate-200 text-slate-600 hover:bg-pink-50 hover:border-pink-200 hover:text-pink-700',
    activeColor: 'bg-pink-50 border-pink-300 text-pink-700 font-semibold',
  },
  {
    key: 'man_matters',
    label: 'Man Matters',
    color: 'border-slate-200 text-slate-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700',
    activeColor: 'bg-blue-50 border-blue-300 text-blue-700 font-semibold',
  },
  {
    key: 'little_joys',
    label: 'Little Joys',
    color: 'border-slate-200 text-slate-600 hover:bg-emerald-50 hover:border-emerald-200 hover:text-emerald-700',
    activeColor: 'bg-emerald-50 border-emerald-300 text-emerald-700 font-semibold',
  },
]

interface BriefResponse {
  id: string
  brand: string
  markdown: string
  generated_at: string
  stats?: object
}

async function fetchStoredBrief(brand: string): Promise<BriefResponse | null> {
  const res = await fetch(`${API_BASE}/api/brief/${brand}`)
  if (res.status === 404) return null
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()
}

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-indigo-500"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function WeeklyBrief() {
  const [selectedBrand, setSelectedBrand] = useState('bebodywise')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: brief, isLoading } = useQuery<BriefResponse | null>({
    queryKey: ['brief', selectedBrand],
    queryFn: () => fetchStoredBrief(selectedBrand),
    retry: false,
    staleTime: 0,
  })

  async function handleGenerate() {
    setIsGenerating(true)
    setGenerateError(null)
    try {
      const res = await fetch(`${API_BASE}/api/brief/generate/${selectedBrand}`, {
        method: 'POST',
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail ?? `Error ${res.status}`)
      }
      // Invalidate the cached GET so the panel refreshes with the new brief
      await queryClient.invalidateQueries({ queryKey: ['brief', selectedBrand] })
    } catch (err) {
      setGenerateError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsGenerating(false)
    }
  }

  const activeBrand = BRANDS.find((b) => b.key === selectedBrand)!

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* ── Panel header ── */}
      <div className="px-4 py-3 border-b border-slate-100 bg-slate-50 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-slate-800">Weekly Brief</span>
          <span className="rounded-full bg-indigo-100 text-indigo-600 text-[10px] font-semibold px-2 py-0.5">
            AI
          </span>
        </div>
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-1.5 text-xs
                     font-semibold text-white hover:bg-indigo-700 disabled:opacity-60
                     disabled:cursor-not-allowed transition-colors"
        >
          {isGenerating ? (
            <>
              <Spinner />
              Generating…
            </>
          ) : (
            <>✨ Generate</>
          )}
        </button>
      </div>

      {/* ── Brand tabs ── */}
      <div className="flex gap-1.5 px-4 pt-3 pb-2">
        {BRANDS.map((b) => (
          <button
            key={b.key}
            onClick={() => {
              setSelectedBrand(b.key)
              setGenerateError(null)
            }}
            className={`flex-1 rounded-md border px-2 py-1 text-[11px] transition-colors
                        ${selectedBrand === b.key ? b.activeColor : b.color}`}
          >
            {b.label}
          </button>
        ))}
      </div>

      {/* ── Content area ── */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {/* Error from generate call */}
        {generateError && (
          <div className="mb-3 rounded-lg bg-red-50 border border-red-200 px-3 py-2.5 text-xs text-red-700">
            <span className="font-semibold">Generation failed: </span>
            {generateError}
          </div>
        )}

        {/* Loading the stored brief */}
        {isLoading && (
          <div className="flex items-center justify-center py-10 gap-2 text-slate-400 text-xs">
            <Spinner />
            Loading brief…
          </div>
        )}

        {/* No brief yet */}
        {!isLoading && !brief && !generateError && (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <span className="text-3xl mb-3">📋</span>
            <p className="text-sm font-semibold text-slate-700 mb-1">No brief yet</p>
            <p className="text-xs text-slate-500 max-w-[200px]">
              Click <strong>Generate</strong> to create an AI-powered competitive brief for{' '}
              <strong>{activeBrand.label}</strong>.
            </p>
            <p className="text-[10px] text-slate-400 mt-2">
              Requires ANTHROPIC_API_KEY in backend/.env
            </p>
          </div>
        )}

        {/* Brief content */}
        {!isLoading && brief && (
          <>
            <div className="flex items-center justify-between mb-3 pt-1">
              <span className="text-[10px] text-slate-400">
                Generated {formatDate(brief.generated_at)}
              </span>
              <span
                className={`text-[10px] font-semibold rounded-full px-2 py-0.5 ${activeBrand.activeColor} border`}
              >
                {activeBrand.label}
              </span>
            </div>
            <SimpleMarkdown content={brief.markdown} />
          </>
        )}
      </div>
    </div>
  )
}
