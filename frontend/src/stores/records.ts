import { defineStore } from 'pinia'
import { ref } from 'vue'
import { categoriesApi, recordsApi } from '@/api'
import { type Record, type Dashboard, type Paginated, type RecordType, Category } from '@/types'

export const useRecordsStore = defineStore('records', () => {
  const records = ref<Record[]>([])
  const total = ref(0)
  const dashboard = ref<Dashboard | null>(null)
  const categories = ref<Category[]>([])
  const loading = ref(false)

  function mockRecords() {
    records.value = [
      {
        id: '1', title: 'Salary', amount: 35000, type: 'income',
        note: 'Monthly salary', date: '2024-04-01',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-1',
        category: { id: 'cat-1', name: 'Salary', icon: '💰', color: '#22c55e', is_default: true },
        created_at: '2024-04-01T09:00:00',
      },
      {
        id: '2', title: 'Rent', amount: 8000, type: 'expense',
        note: 'Monthly rent', date: '2024-04-02',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-2',
        category: { id: 'cat-2', name: 'Housing', icon: '🏠', color: '#f43f5e', is_default: true },
        created_at: '2024-04-02T09:00:00',
      },
      {
        id: '3', title: 'Groceries', amount: 1200, type: 'expense',
        note: 'Weekly groceries', date: '2024-04-03',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-3',
        category: { id: 'cat-3', name: 'Food', icon: '🍔', color: '#f97316', is_default: true },
        created_at: '2024-04-03T09:00:00',
      },
      {
        id: '4', title: 'Freelance project', amount: 12000, type: 'income',
        note: 'Web design project', date: '2024-04-05',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-4',
        category: { id: 'cat-4', name: 'Freelance', icon: '💻', color: '#6366f1', is_default: false },
        created_at: '2024-04-05T09:00:00',
      },
      {
        id: '5', title: 'Electric bill', amount: 850, type: 'expense',
        note: 'April electricity', date: '2024-04-06',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-5',
        category: { id: 'cat-5', name: 'Utilities', icon: '⚡', color: '#eab308', is_default: true },
        created_at: '2024-04-06T09:00:00',
      },
      {
        id: '6', title: 'Dinner out', amount: 650, type: 'expense',
        note: 'Restaurant with friends', date: '2024-04-07',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-3',
        category: { id: 'cat-3', name: 'Food', icon: '🍔', color: '#f97316', is_default: true },
        created_at: '2024-04-07T09:00:00',
      },
      {
        id: '7', title: 'Netflix', amount: 299, type: 'expense',
        note: 'Monthly subscription', date: '2024-04-08',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-6',
        category: { id: 'cat-6', name: 'Entertainment', icon: '🎬', color: '#ec4899', is_default: true },
        created_at: '2024-04-08T09:00:00',
      },
      {
        id: '8', title: 'Stock dividend', amount: 5000, type: 'income',
        note: 'Q1 dividend payout', date: '2024-04-09',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-7',
        category: { id: 'cat-7', name: 'Investment', icon: '📈', color: '#22c55e', is_default: false },
        created_at: '2024-04-09T09:00:00',
      },
      {
        id: '9', title: 'Taxi', amount: 320, type: 'expense',
        note: 'Ride to airport', date: '2024-04-10',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-8',
        category: { id: 'cat-8', name: 'Transport', icon: '🚕', color: '#0ea5e9', is_default: true },
        created_at: '2024-04-10T09:00:00',
      },
      {
        id: '10', title: 'Coffee', amount: 120, type: 'expense',
        note: 'Morning coffee', date: '2024-04-11',
        is_scanned: false, owner_id: 'user-1',
        category_id: 'cat-3',
        category: { id: 'cat-3', name: 'Food', icon: '🍔', color: '#f97316', is_default: true },
        created_at: '2024-04-11T09:00:00',
      },
    ] as Record[]

    total.value = records.value.length

    dashboard.value = {
      period_summary: {
        total_income: 52000,
        total_expense: 31500,
        net: 20500,
        record_count: records.value.length,
      },
      monthly_trends: [
        { year: 2024, month: 1, income: 40000, expense: 28000, net: 12000 },
        { year: 2024, month: 2, income: 45000, expense: 30000, net: 15000 },
        { year: 2024, month: 3, income: 48000, expense: 29500, net: 18500 },
        { year: 2024, month: 4, income: 52000, expense: 31500, net: 20500 },
      ],
      category_breakdown: [
        { category_name: 'Food',          total: 8500,  count: 3, percentage: 27 },
        { category_name: 'Housing',       total: 8000,  count: 1, percentage: 25 },
        { category_name: 'Utilities',     total: 2000,  count: 1, percentage: 6  },
        { category_name: 'Entertainment', total: 1500,  count: 1, percentage: 5  },
        { category_name: 'Transport',     total: 1200,  count: 1, percentage: 4  },
        { category_name: 'Salary',        total: 35000, count: 1, percentage: 67 },
        { category_name: 'Freelance',     total: 12000, count: 1, percentage: 23 },
        { category_name: 'Investment',    total: 5000,  count: 1, percentage: 10 },
      ],
      recent_records: records.value.slice(0, 8),
    } as Dashboard
  }

  async function fetchPersonal(params?: {
    skip?: number; limit?: number; type?: RecordType
    category_id?: string; date_from?: string; date_to?: string
  }) {
    loading.value = true
    try {
      const { data } = await recordsApi.listPersonal(params)
      records.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchGroup(groupId: string, params?: {
    skip?: number; limit?: number; type?: RecordType
    category_id?: string; member_id?: string
    date_from?: string; date_to?: string
  }) {
    loading.value = true
    try {
      const { data } = await recordsApi.listGroup(groupId, params)
      records.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    const { data } = await categoriesApi.list()
    categories.value = data
  }

  async function fetchPersonalDashboard(params?: { date_from?: string; date_to?: string }) {
    const { data } = await recordsApi.personalDashboard(params)
    dashboard.value = data
  }

  async function fetchGroupDashboard(groupId: string, params?: { date_from?: string; date_to?: string }) {
    const { data } = await recordsApi.groupDashboard(groupId, params)
    dashboard.value = data
  }

  async function createRecord(payload: any) {
    const { data } = await recordsApi.create(payload)
    records.value.unshift(data)
    total.value++
    return data
  }

  async function updateRecord(id: string, payload: any) {
    const { data } = await recordsApi.update(id, payload)
    const idx = records.value.findIndex(r => r.id === id)
    if (idx !== -1) records.value[idx] = data
    return data
  }

  async function deleteRecord(id: string) {
    await recordsApi.delete(id)
    records.value = records.value.filter(r => r.id !== id)
    total.value--
  }

  return {
    records, total, dashboard, categories, loading,
    mockRecords, fetchPersonal, fetchGroup, fetchCategories,
    fetchPersonalDashboard, fetchGroupDashboard,
    createRecord, updateRecord, deleteRecord,
  }
})
