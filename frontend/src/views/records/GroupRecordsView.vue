<template>
  <div class="p-12 space-y-5 max-w-6xl mx-auto">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">{{ group?.name }}</h1>
        <p v-if="group?.description" class="text-sm text-gray-400 mt-0.5">{{ group.description }}</p>
      </div>
      <button v-if="canRecord" @click="showForm = true" class="btn-primary">
        <PlusIcon class="w-4 h-4" /> Add Record
      </button>
    </div>

    <!-- Viewer notice -->
    <div v-if="!canRecord" class="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-center gap-3">
      <EyeIcon class="w-4 h-4 text-amber-600 flex-shrink-0" />
      <p class="text-sm text-amber-700">You have <strong>viewer</strong> access — you can view records but cannot add or edit them.</p>
    </div>

    <!-- Filters -->
    <div class="card p-4 flex flex-wrap gap-3 items-center">
      <!-- Member -->
      <select v-model="filter.member_id" @change="load" class="input w-auto text-sm py-2">
        <option value="">All Members</option>
        <option v-for="m in group?.members" :key="m.user_id" :value="m.user_id">
          {{ m.user?.username }}
        </option>
      </select>

      <!-- Category -->
      <select v-model="filter.category_id" @change="load" class="input w-auto text-sm py-2">
        <option value="">All Categories</option>
        <option v-for="c in mockCategories" :key="c.id" :value="c.id">
          {{ c.icon }} {{ c.name }}
        </option>
      </select>

      <!-- Type -->
      <select v-model="filter.type" @change="load" class="input w-auto text-sm py-2">
        <option value="">All Types</option>
        <option value="income">Income</option>
        <option value="expense">Expense</option>
      </select>

      <!-- Date -->
      <div class="flex items-center gap-2">
        <input v-model="filter.date_from" type="date" @change="load" class="input w-auto text-sm py-2" />
        <span class="text-gray-400 font-medium select-none">—</span>
        <input v-model="filter.date_to" type="date" @change="load" class="input w-auto text-sm py-2" />
      </div>

      <button @click="clearFilters" class="btn-ghost text-sm py-2">Clear</button>
    </div>

    <!-- Records list -->
    <div class="card divide-y divide-slate-50">
      <div v-if="loading" class="p-4 space-y-2">
        <div v-for="i in 5" :key="i" class="h-12 bg-slate-50 rounded-xl animate-pulse" />
      </div>
      <template v-else-if="records.length">
        <RecordRow
          v-for="r in records" :key="r.id"
          :record="r"
          :read-only="!canRecord"
          @edit="startEdit(r)"
          @delete="confirmDelete(r)"
        />
      </template>
      <div v-else class="p-12 text-center">
        <DocumentTextIcon class="w-12 h-12 text-slate-200 mx-auto mb-3" />
        <p class="text-ink-400 text-sm">No records in this group yet.</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > limit" class="flex items-center justify-between text-sm text-ink-400">
      <span>Showing {{ skip + 1 }}–{{ Math.min(skip + limit, total) }} of {{ total }}</span>
      <div class="flex gap-2">
        <button :disabled="skip === 0" @click="prevPage" class="btn-ghost py-1.5 px-3 text-xs disabled:opacity-40">← Prev</button>
        <button :disabled="skip + limit >= total" @click="nextPage" class="btn-ghost py-1.5 px-3 text-xs disabled:opacity-40">Next →</button>
      </div>
    </div>
  </div>

  <RecordFormModal
    v-if="showForm"
    :edit-record="editingRecord"
    :locked-group-id="id"
    @close="closeForm"
    @saved="onSaved"
  />

  <ConfirmDialog
    v-if="deletingRecord"
    title="Delete Record"
    :message="`Delete &quot;${deletingRecord.title}&quot;? This cannot be undone.`"
    @confirm="doDelete"
    @cancel="deletingRecord = null"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PlusIcon, DocumentTextIcon, EyeIcon } from '@heroicons/vue/24/outline'
import { useRecordsStore } from '@/stores/records'
import { useGroupsStore } from '@/stores/groups'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import RecordRow from '@/components/records/RecordRow.vue'
import RecordFormModal from '@/components/records/RecordFormModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import type { Record } from '@/types'

const route = useRoute()
const id = route.params.id as string
const recordsStore = useRecordsStore()
const groupsStore = useGroupsStore()
const authStore = useAuthStore()

const { records, total, loading } = storeToRefs(recordsStore)
const { currentGroup: group } = storeToRefs(groupsStore)

const showForm = ref(false)
const editingRecord = ref<Record | undefined>()
const deletingRecord = ref<Record | null>(null)
const skip = ref(0)
const limit = 20
const filter = ref({
  member_id: '',
  category_id: '',
  type: '',
  date_from: '',
  date_to: '',
})

const mockCategories = [
  { id: 'cat-1', name: 'Salary',        icon: '💰' },
  { id: 'cat-2', name: 'Housing',       icon: '🏠' },
  { id: 'cat-3', name: 'Food',          icon: '🍔' },
  { id: 'cat-4', name: 'Freelance',     icon: '💻' },
  { id: 'cat-5', name: 'Utilities',     icon: '⚡' },
  { id: 'cat-6', name: 'Entertainment', icon: '🎬' },
  { id: 'cat-7', name: 'Investment',    icon: '📈' },
  { id: 'cat-8', name: 'Transport',     icon: '🚕' },
]

const canRecord = computed(() => {
  const me = group.value?.members.find(m => m.user_id === authStore.user?.id)
  return me && me.role !== 'viewer'
})

async function load() {
  await recordsStore.fetchGroup(id, {
    skip: skip.value, limit,
    type: filter.value.type as any || undefined,
    category_id: filter.value.category_id || undefined,
    member_id: filter.value.member_id || undefined,
    date_from: filter.value.date_from || undefined,
    date_to: filter.value.date_to || undefined,
  })
}

function clearFilters() {
  filter.value = { member_id: '', category_id: '', type: '', date_from: '', date_to: '' }
  skip.value = 0
  load()
}

function prevPage() { skip.value = Math.max(0, skip.value - limit); load() }
function nextPage() { skip.value += limit; load() }
function startEdit(r: Record) { editingRecord.value = r; showForm.value = true }
function confirmDelete(r: Record) { deletingRecord.value = r }
function closeForm() { showForm.value = false; editingRecord.value = undefined }

async function onSaved() { closeForm(); await load() }
async function doDelete() {
  if (!deletingRecord.value) return
  await recordsStore.deleteRecord(deletingRecord.value.id)
  deletingRecord.value = null
}

onMounted(async () => {
  groupsStore.mockGroup(id)
  await load()
})
</script>
