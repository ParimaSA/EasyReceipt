<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 class="font-display text-lg font-semibold text-ink-900">
            {{ editRecord ? 'Edit Record' : 'New Record' }}
          </h2>
          <button @click="$emit('close')" class="p-2 rounded-lg hover:bg-gray-100 text-ink-400">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>

        <!-- OCR scan area (new records only) -->
        <div v-if="!editRecord" class="px-6 pt-4">
          <label
            :class="['border-2 border-dashed rounded-xl p-4 flex flex-col items-center gap-2 cursor-pointer transition-colors',
              scanning ? 'border-amber-400 bg-amber-50' : 'border-gray-200 hover:border-amber-300 hover:bg-amber-50/50']"
          >
            <input type="file" accept="image/*" class="hidden" @change="handleScan" />
            <CameraIcon class="w-6 h-6 text-ink-400" />
            <span class="text-xs font-medium text-ink-500">
              {{ scanning ? 'Scanning receipt…' : 'Upload receipt to auto-fill' }}
            </span>
          </label>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
          <!-- Type toggle -->
          <div class="flex rounded-xl bg-gray-100 p-1 gap-1">
            <button type="button" v-for="t in ['income','expense']" :key="t"
              @click="form.type = t as any"
              :class="['flex-1 py-2 rounded-lg text-sm font-semibold transition-all',
                form.type === t
                  ? (t === 'income' ? 'bg-white text-sage-600 shadow-sm' : 'bg-white text-coral-600 shadow-sm')
                  : 'text-ink-400 hover:text-ink-600']"
            >
              {{ t.charAt(0).toUpperCase() + t.slice(1) }}
            </button>
          </div>

          <div>
            <label class="label">Title</label>
            <input v-model="form.title" required class="input" placeholder="e.g. Grocery shopping" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Amount (฿)</label>
              <input v-model.number="form.amount" type="number" step="0.01" min="0.01" required class="input" placeholder="0.00" />
            </div>
            <div>
              <label class="label">Date</label>
              <input v-model="form.date" type="date" required class="input" />
            </div>
          </div>

          <div v-if="form.type !== 'income'">
            <div class="flex w-full justify-between">
              <label class="label">Category</label>
              <button type="button" @click="showCategoryManager = true" class="text-xs text-amber-600 hover:underline">
                Manage
              </button>
            </div>
            <select v-model="form.category_id" class="input">
              <option value="">— None —</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">
                {{ c.icon }} {{ c.name }}
              </option>
            </select>
          </div>

          <div v-if="groups.length && !editRecord">
            <label class="label">Post to Group (optional)</label>
            
            <!-- locked if add record from the group page -->
            <div v-if="lockedGroupId" class="input bg-gray-50 text-ink-500 cursor-not-allowed">
              {{ groups.find(g => g.id === lockedGroupId)?.name ?? lockedGroupId }}
            </div>

            <select v-else v-model="form.group_id" class="input">
              <option value="">— Personal —</option>
              <option v-for="g in recordableGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
          </div>

          <div>
            <label class="label">Note</label>
            <textarea v-model="form.note" rows="2" class="input resize-none" placeholder="Optional note…" />
          </div>

          <p v-if="error" class="text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg">{{ error }}</p>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="$emit('close')" class="btn-ghost flex-1">Cancel</button>
            <button type="submit" :disabled="submitting" class="btn-primary flex-1">
              {{ submitting ? 'Saving…' : (editRecord ? 'Update' : 'Add Record') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <CategoryManagerModal
    v-if="showCategoryManager"
    :categories="categories"
    @close="showCategoryManager = false"
    @updated="categories = $event"
  />
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { XMarkIcon, CameraIcon } from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { categoriesApi, recordsApi } from '@/api'
import { useGroupsStore } from '@/stores/groups'
import { useAuthStore } from '@/stores/auth'
import { useCategoriesStore } from '@/stores/categories'
import type { Record, RecordType } from '@/types'
import CategoryManagerModal from './CategoryManagerModal.vue'

const props = defineProps<{ editRecord?: Record, lockedGroupId?: string }>()
const emit = defineEmits<{ close: []; saved: [record: Record] }>()

const authStore = useAuthStore()
const groupsStore = useGroupsStore()
const catStore = useCategoriesStore()
const { categories } = storeToRefs(catStore)

const scanning = ref(false)
const submitting = ref(false)
const error = ref('')

const showCategoryManager = ref(false)

const form = ref({
  title: '',
  amount: 0,
  type: 'expense' as RecordType,
  date: format(new Date(), 'yyyy-MM-dd'),
  category_id: '',
  group_id: props.lockedGroupId ?? '',
  note: '',
})

const groups = computed(() => groupsStore.groups)
const recordableGroups = computed(() =>
  groups.value.filter(g => {
    const me = g.members.find(m => m.user_id === authStore.user?.id)
    return me && me.role !== 'viewer'
  })
)

watch(() => props.editRecord, (r) => {
  if (r) {
    form.value = {
      title: r.title,
      amount: r.amount,
      type: r.type,
      date: format(new Date(r.date), 'yyyy-MM-dd'),
      category_id: r.category_id ?? '',
      group_id: r.group_id ?? '',
      note: r.note ?? '',
    }
  }
}, { immediate: true })

onMounted(async () => {
  const { data } = await categoriesApi.list()
  categories.value = data
})

async function handleScan(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  scanning.value = true
  try {
    const { data } = await recordsApi.scan(file)
    if (data.title) form.value.title = data.title
    if (data.amount) form.value.amount = data.amount
    if (data.date) form.value.date = format(new Date(data.date), 'yyyy-MM-dd')
  } catch { /* silently ignore */ }
  finally { scanning.value = false }
}

async function handleSubmit() {
  error.value = ''
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      date: new Date(form.value.date).toISOString(),
      category_id: form.value.category_id || undefined,
      group_id: form.value.group_id || undefined,
    }
    let record: Record
    if (props.editRecord) {
      const { data } = await import('@/api').then(m => m.recordsApi.update(props.editRecord!.id, payload))
      record = data
    } else {
      const { data } = await import('@/api').then(m => m.recordsApi.create(payload))
      record = data
    }
    emit('saved', record)
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Failed to save record.'
  } finally {
    submitting.value = false
  }
}
</script>
