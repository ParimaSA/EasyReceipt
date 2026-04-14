<template>
  <div class="p-12 space-y-5 max-w-6xl mx-auto">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">My Records</h1>
      <button @click="showForm = true" class="btn-primary">
        <PlusIcon class="w-4 h-4" /> Add Record
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4 flex flex-wrap gap-3 items-center">
      <!-- Group -->
      <select v-model="filter.group_id" @change="load" class="input w-auto text-sm py-2">
        <option value="">All Groups</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>

      <!-- Category -->
      <select v-model="filter.category_id" @change="load" class="input w-auto text-sm py-2">
        <option value="">All Categories</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">
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
        <input
          v-model="filter.date_from" type="date" @change="load"
          class="input w-auto text-sm py-2"
          placeholder="Start date"
        />
        <span class="text-gray-400 font-medium select-none">—</span>
        <input
          v-model="filter.date_to" type="date" @change="load"
          class="input w-auto text-sm py-2"
          placeholder="End date"
        />
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
          @edit="startEdit(r)"
          @delete="confirmDelete(r)"
        />
      </template>

      <div v-else class="p-12 text-center">
        <DocumentTextIcon class="w-12 h-12 text-slate-200 mx-auto mb-3" />
        <p class="text-gray-400 text-sm">No records found.</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > limit" class="flex items-center justify-between text-sm text-gray-400">
      <span>Showing {{ skip + 1 }}–{{ Math.min(skip + limit, total) }} of {{ total }}</span>
      <div class="flex gap-2">
        <button :disabled="skip === 0" @click="prevPage" class="btn-ghost py-1.5 px-3 text-xs disabled:opacity-40">← Prev</button>
        <button :disabled="skip + limit >= total" @click="nextPage" class="btn-ghost py-1.5 px-3 text-xs disabled:opacity-40">Next →</button>
      </div>
    </div>
  </div>

  <!-- Modals -->
  <RecordFormModal
    v-if="showForm"
    :edit-record="editingRecord"
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
import { ref, onMounted } from 'vue'
import { PlusIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'
import { useRecordsStore } from '@/stores/records'
import { useGroupsStore } from '@/stores/groups'
import { storeToRefs } from 'pinia'
import RecordRow from '@/components/records/RecordRow.vue'
import RecordFormModal from '@/components/records/RecordFormModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import type { Record } from '@/types'

const recordsStore = useRecordsStore()
const groupsStore = useGroupsStore()

const { records, total, categories, loading } = storeToRefs(recordsStore)
const { groups } = storeToRefs(groupsStore)

const showForm = ref(false)
const editingRecord = ref<Record | undefined>()
const deletingRecord = ref<Record | null>(null)
const skip = ref(0)
const limit = 20

const filter = ref({
  group_id: '',
  category_id: '',
  type: '',
  date_from: '',
  date_to: '',
})

async function load() {
  await groupsStore.fetchGroups()
  await recordsStore.fetchCategories()
  await recordsStore.fetchPersonal({
    skip: skip.value,
    limit,
    type: filter.value.type as any || undefined,
    category_id: filter.value.category_id || undefined,
    date_from: filter.value.date_from || undefined,
    date_to: filter.value.date_to || undefined,
  })
}

function clearFilters() {
  filter.value = { group_id: '', category_id: '', type: '', date_from: '', date_to: '' }
  skip.value = 0
  load()
}

function prevPage() { skip.value = Math.max(0, skip.value - limit); load() }
function nextPage() { skip.value += limit; load() }

function startEdit(r: Record) { editingRecord.value = r; showForm.value = true }
function confirmDelete(r: Record) { deletingRecord.value = r }
function closeForm() { showForm.value = false; editingRecord.value = undefined }

async function onSaved(_record: Record) {
  closeForm()
  skip.value = 0
  await load()
}

async function doDelete() {
  if (!deletingRecord.value) return
  await recordsStore.deleteRecord(deletingRecord.value.id)
  deletingRecord.value = null
}

onMounted(load)
</script>