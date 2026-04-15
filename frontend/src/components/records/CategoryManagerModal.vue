<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 class="text-lg font-semibold">Categories</h2>
          <button @click="$emit('close')" class="p-2 rounded-lg hover:bg-gray-100">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>

        <div class="px-6 py-3 space-y-2 max-h-52 overflow-y-auto">
          <div v-if="!catStore.customCategories.length" class="text-center py-4 text-sm text-gray-400">
            No custom categories yet.
          </div>
          
          <div
            v-for="c in catStore.customCategories" :key="c.id"
            class="flex items-center justify-between gap-3 px-3 py-2 rounded-xl border border-gray-100 hover:bg-gray-50"
          >
            <div class="flex items-center gap-2">
              <span
                class="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
                :style="{ backgroundColor: c.color + '30', color: c.color }"
              >{{ c.icon }}</span>
              <span class="text-sm font-medium">{{ c.name }}</span>
            </div>
            
            <button
              @click="categoryToDelete = c"
              class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
            >
              <TrashIcon class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div class="border-t border-slate-100 px-6 py-4">
          <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">New Category</p>
          <div class="space-y-3">
            <div class="flex gap-3">
              <div class="flex-1">
                <label class="label">Name</label>
                <input v-model="newCat.name" class="input" placeholder="e.g. Transport" />
              </div>
              <div class="w-20">
                <label class="label">Icon</label>
                <input v-model="newCat.icon" class="input text-center" placeholder="📦" />
              </div>
            </div>
            <div>
              <label class="label">Color</label>
              <div class="flex items-center gap-2">
                <input type="color" v-model="newCat.color" class="w-10 h-10 rounded-lg border border-gray-200 cursor-pointer p-0.5" />
                <div class="flex gap-1.5 flex-wrap">
                  <button
                    v-for="preset in colorPresets" :key="preset"
                    @click="newCat.color = preset"
                    :style="{ backgroundColor: preset }"
                    :class="['w-6 h-6 rounded-full border-2 transition-all', newCat.color === preset ? 'border-gray-600 scale-110' : 'border-transparent']"
                  />
                </div>
              </div>
            </div>
            <p v-if="createError" class="text-red-500 text-xs">{{ createError }}</p>
            <button
              @click="handleCreate"
              :disabled="creating || !newCat.name"
              class="btn-primary w-full"
            >
              {{ creating ? 'Adding…' : '+ Add Category' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <ConfirmDialog
    v-if="categoryToDelete"
    title="Delete Category"
    :message="`Delete category &quot;${categoryToDelete.name}&quot;? This cannot be undone.`"
    @confirm="confirmDelete"
    @cancel="categoryToDelete = null"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { XMarkIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useCategoriesStore } from '@/stores/categories'
import type { Category } from '@/types'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

defineEmits<{ close: [] }>()

const catStore = useCategoriesStore()
const categoryToDelete = ref<Category | null>(null)
const creating = ref(false)
const createError = ref('')
const newCat = ref({ name: '', icon: '📦', color: '#f59e0b' })
const colorPresets = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#f97316', '#06b6d4', '#ec4899']

async function handleCreate() {
  if (!newCat.value.name) return
  creating.value = true
  createError.value = ''
  try {
    await catStore.createCategory(newCat.value)
    newCat.value = { name: '', icon: '📦', color: '#f59e0b' }
  } catch (e: any) {
    createError.value = e.response?.data?.detail ?? 'Failed to create category.'
  } finally {
    creating.value = false
  }
}

async function confirmDelete() {
  if (!categoryToDelete.value) return
  try {
    await catStore.deleteCategory(categoryToDelete.value.id)
  } finally {
    categoryToDelete.value = null
  }
}
</script>