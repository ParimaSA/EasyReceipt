export type UserRole = 'personal' | 'leader' | 'viewer'
export type GroupMemberRole = 'leader' | 'member' | 'viewer'
export type RecordType = 'income' | 'expense'

export interface User {
  id: string
  email: string
  username: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface Category {
  id: string
  name: string
  icon?: string
  color?: string
  is_default: boolean
  owner_id?: string
}

export interface Record {
  id: string
  title: string
  amount: number
  type: RecordType
  note?: string
  date: string
  receipt_image_url?: string
  is_scanned: boolean
  owner_id: string
  group_id?: string
  category_id?: string
  category?: Category
  owner?: { id: string; username: string; }
  created_at: string
  updated_at?: string
}

export interface GroupMember {
  id: string
  user_id: string
  group_id: string
  role: GroupMemberRole
  joined_at: string
  user?: { id: string; username: string; }
}

export interface Group {
  id: string
  name: string
  description?: string
  leader_id: string
  is_active: boolean
  created_at: string
  members: GroupMember[]
}

export interface Invitation {
  id: string
  group_id: string
  token: string
  invited_role: GroupMemberRole
  is_active: boolean
  max_uses?: number
  use_count: number
  expires_at?: string
  created_at: string
  invite_url?: string
}

export interface PeriodSummary {
  total_income: number
  total_expense: number
  net: number
  record_count: number
}

export interface CategoryBreakdown {
  category_id?: string
  category_name: string
  total: number
  count: number
  percentage: number
}

export interface MonthlyTrend {
  year: number
  month: number
  income: number
  expense: number
  net: number
}

export interface Dashboard {
  period_summary: PeriodSummary
  category_breakdown: CategoryBreakdown[]
  monthly_trends: MonthlyTrend[]
  recent_records: Record[]
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}
