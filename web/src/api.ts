import type {
  Analysis, AnnouncementItem, HealthOut, Interpretation, ReportItem,
  SearchItem, SnapshotMeta,
} from './types'

const BASE = '/api'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!r.ok) {
    let detail: any = null
    try { detail = await r.json() } catch { /* ignore */ }
    const err = new Error(detail?.hint || detail?.error || `HTTP ${r.status}`)
    ;(err as any).status = r.status
    ;(err as any).detail = detail
    throw err
  }
  return r.json()
}

export const api = {
  health: () => req<HealthOut>('/health'),
  meta: () => req<SnapshotMeta>('/snapshot/meta'),
  search: (q: string, limit = 10) =>
    req<{ q: string; items: SearchItem[] }>(
      `/stocks/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  analysis: (code: string) => req<Analysis>(`/analysis/${code}`),
  announcements: (code: string, limit = 20) =>
    req<{ items: AnnouncementItem[]; error: string | null }>(
      `/announcements/${code}?limit=${limit}`),
  reports: (code: string, limit = 20) =>
    req<{ items: ReportItem[]; rating_distribution: Record<string, number>; error: string | null; note: string | null }>(
      `/research-reports/${code}?limit=${limit}`),
  interpret: (code: string, force = false) =>
    req<Interpretation>(`/interpretation/${code}`, {
      method: 'POST', body: JSON.stringify({ force_refresh: force }),
    }),
  histogram: (bins = 40) =>
    req<{ edges: number[]; counts: number[]; core_min: number; core_median: number; core_max: number }>(
      `/universe/histogram?bins=${bins}`),
}
