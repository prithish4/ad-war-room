import type { AdsResponse, CompetitorsResponse } from './types'

export const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

export async function fetchAds(params: {
  brand?: string
  ad_format?: string
}): Promise<AdsResponse> {
  const url = new URL(`${API_BASE}/api/ads`)
  url.searchParams.set('limit', '200')
  if (params.brand) url.searchParams.set('brand', params.brand)
  if (params.ad_format) url.searchParams.set('ad_format', params.ad_format)

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`Failed to fetch ads: ${res.status}`)
  return res.json()
}

export async function fetchCompetitors(brand?: string): Promise<CompetitorsResponse> {
  const url = new URL(`${API_BASE}/api/competitors`)
  if (brand) url.searchParams.set('brand', brand)

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`Failed to fetch competitors: ${res.status}`)
  return res.json()
}
