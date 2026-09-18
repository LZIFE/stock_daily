/** 与后端 app/schemas.py 对齐。改后端契约时同步这里。 */

export interface HealthOut {
  status: string
  snapshot_ready: boolean
  asof: string | null
  universe_size: number | null
  scorer_sha256: string | null
  panel_sha256: string | null
  ai_available: boolean
  ai_model: string | null
  version: string
  hint: string | null
}

export interface Evidence {
  window: string
  n: number
  base_bad_rate: number
  auc: number
  quintiles: number[]
  quintile_edges: number[]
}

export interface SnapshotMeta {
  asof: string | null
  built_at: string | null
  universe_size: number | null
  n_scored: number | null
  band_distribution: Record<string, number>
  coverage: Record<string, number>
  core_score: Record<string, number>
  core_books: string[]
  evidence: Evidence | null
  thresholds: Threshold[]
  disclaimers: string[]
}

export interface SearchItem {
  code: string
  name: string
  price: number | null
  band: string | null
  core_score: number | null
  core_pctl: number | null
}

export interface BookScore {
  name: string
  /** null = 算不出来。绝不能显示成 50。 */
  score: number | null
  available: boolean
  core: boolean
  cluster: string
  rule: string
}

export interface BadRate {
  bin_lo: number
  bin_hi: number
  n: number
  bad_rate: number
  quintile: string
  quintile_bad_rate: number | null
  base_bad_rate: number
  auc: number
  window: string
  n_window: number
}

export interface HistoryPoint {
  date: string
  core_score: number
  pctl: number
  source: string
}

export interface HistoryOut {
  points: HistoryPoint[]
  n: number
  min: number
  max: number
  delta: number
  pctl_now: number | null
  pctl_median: number | null
}

export interface ClusterScore {
  cluster: string
  label: string
  desc: string
  score: number | null
  universe_median: number | null
  diff: number | null
  n_books: number
  n_available: number
  books: string[]
  has_core: boolean
}

export interface Threshold {
  label: string
  base_bad_rate: number
  q1: number
  q5: number
  spread_pp: number
  ratio: number
  auc: number
  quintiles: number[]
}

export interface Analysis {
  code: string
  name: string
  asof: string | null
  price: number | null
  change_pct: number | null
  band: string | null
  core_score: number | null
  core_pctl: number | null
  n_tied: number | null
  consensus_score: number | null
  divergence: number | null
  coverage_pct: number | null
  core_coverage_pct: number | null
  pe_available: boolean
  loss_maker: boolean
  quality_bad: boolean
  core_imputed_books: string[]
  n_books_available: number | null
  n_books_total: number | null
  soft_demote: string[]
  flags: string[]
  position_cap_pct: number | null
  tech: Record<string, number | null>
  fin: Record<string, number | null>
  pct: Record<string, number | null>
  period: Record<string, string | null>
  books: BookScore[]
  clusters: ClusterScore[]
  history: HistoryOut | null
  badrate: BadRate | null
  disclaimers: string[]
}

export interface AnnouncementItem {
  art_code: string
  notice_date: string
  title: string
  columns: string[]
}

export interface ReportItem {
  publish_date: string
  org: string
  title: string
  rating: string
  industry: string
}

export interface Interpretation {
  code: string
  asof: string | null
  cached: boolean
  generated_at: string | null
  model: string | null
  prompt_version: string | null
  degraded: boolean
  warnings: string[]
  sections: {
    headline?: string
    core_book_explanation?: { book: string; score: number; reading: string }[]
    consensus_panel?: { summary?: string; divergence_reading?: string }
    event_scan?: { date: string; title: string; impact: string; why: string; unverified?: boolean }[]
    risks_rules_cannot_see?: string[]
    what_would_change_the_verdict?: string[]
    data_limits?: string[]
    verdict_restate?: { band: string; core_score: number; core_pctl: number; note: string }
  } | null
  sources: { kind: string; title: string; date: string; org?: string }[]
  disclaimers: string[]
}

// ---------------------------------------------------------------- 全市场榜单
export interface ScreenRow {
  code: string
  name: string
  price: number | null
  change_pct: number | null
  band: string | null
  core_score: number | null
  core_pctl: number | null
  n_tied: number | null
  consensus_score: number | null
  divergence: number | null
  delta3: number | null
  sort_value: number | null
  badrate: BadRate | null
  flags: string[]
  soft_demote: string[]
  core_imputed_books: string[]
  pe_available: boolean
  loss_maker: boolean
  industries: string[]
}

export interface ScreenMeta {
  kind: string
  title: string
  lede: string
  n_universe: number
  n_returned: number
  industry_coverage_note: string | null
  tiebreak_note: string | null
  tiebreak_key: string | null
}

export interface ScreenOut {
  meta: ScreenMeta
  rows: ScreenRow[]
  disclaimer: string
}

export interface ScreenKind { kind: string; title: string; lede: string }

// ---------------------------------------------------------------- 决策日志
export interface JournalVerify {
  status: string
  progress?: number
  n_observed?: number
  horizon_days?: number
  base_price?: number
  base_date?: string
  max_drawdown_pct?: number
  return_pct?: number
  last_date?: string
  hit_bad?: boolean
  hit_date?: string | null
  note?: string
}

export interface JournalEntry {
  id: string
  code: string
  name: string
  created_at: string
  date: string
  note: string
  price_at_entry: number | null
  band_at_entry: string | null
  core_score_at_entry: number | null
  core_pctl_at_entry: number | null
  consensus_at_entry: number | null
  divergence_at_entry: number | null
  expected_bad_rate: number | null
  base_bad_rate: number | null
  soft_demote: string[]
  flags: string[]
  core_imputed_books: string[]
  asof: string | null
  verify: JournalVerify
  band_now: string | null
  core_score_now: number | null
  core_pctl_now: number | null
  band_changed: boolean
}

export interface JournalSummary {
  n_total: number
  n_observed: number
  n_pending: number
  observed_bad_rate: number | null
  expected_bad_rate_mean: number | null
  base_bad_rate: number | null
  horizon_days: number
  bad_threshold_pct: number
  note: string
}

export interface JournalOut { entries: JournalEntry[]; summary: JournalSummary }
