export interface Ad {
  id: string
  ad_id: string
  competitor_name: string
  competitor_page_id: string
  brand: string
  vertical: string
  ad_format: 'static' | 'video' | 'carousel'
  message_theme: string
  emotional_tone: string
  headline: string
  body_text: string
  cta: string
  platform: string
  estimated_spend_min: number
  estimated_spend_max: number
  start_date: string
  end_date: string | null
  is_active: boolean
  days_running: number
  num_cards: number | null
  country: string
  source: string
  created_at: string
}

export interface Competitor {
  competitor_name: string
  brand: string
  vertical: string
  total_ads: number
  active_ads: number
  avg_spend: number
  max_days_running: number
  top_theme: string | null
}

export interface AdsResponse {
  data: Ad[]
  total: number
  count: number
  limit: number
  offset: number
}

export interface CompetitorsResponse {
  data: Competitor[]
  count: number
}

export type BrandFilter = 'bebodywise' | 'man_matters' | 'little_joys' | ''
export type FormatFilter = 'static' | 'video' | 'carousel' | ''
export type DateRangeFilter = '7' | '30' | '60' | 'all'
