import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { categoriesApi } from '@/api'
import { type Category } from '@/types'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const customCategories = computed(() => 
    categories.value.filter(cat => !cat.is_default)
  )
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      const { data } = await categoriesApi.list()
      categories.value = data
    } finally {
      loading.value = false
    }
  }

  async function createCategory(payload: any) {
    const { data } = await categoriesApi.create(payload)
    categories.value.unshift(data)
    return data
  }

  async function deleteCategory(id: string) {
    await categoriesApi.delete(id)
    categories.value = categories.value.filter(c => c.id !== id)
  }

  return {
    categories, customCategories, 
    fetchCategories, createCategory, deleteCategory
  }
})
