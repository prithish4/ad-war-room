import { create } from 'zustand'
import type { BrandFilter, DateRangeFilter, FormatFilter } from '../types'

interface FilterState {
  brand: BrandFilter
  format: FormatFilter
  dateRange: DateRangeFilter
  setBrand: (b: BrandFilter) => void
  setFormat: (f: FormatFilter) => void
  setDateRange: (d: DateRangeFilter) => void
  resetFilters: () => void
}

export const useFilterStore = create<FilterState>((set) => ({
  brand: '',
  format: '',
  dateRange: 'all',
  setBrand: (brand) => set({ brand }),
  setFormat: (format) => set({ format }),
  setDateRange: (dateRange) => set({ dateRange }),
  resetFilters: () => set({ brand: '', format: '', dateRange: 'all' }),
}))
