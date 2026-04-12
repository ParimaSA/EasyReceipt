<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <h2 class="text-lg font-semibold">Create Group</h2>
        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="label">Group Name</label>
            <input v-model="form.name" required class="input" placeholder="e.g. Family Budget" />
          </div>
          <div>
            <label class="label">Group Icon (Optional)</label>
            <input v-model="form.icon" class="input" placeholder="Optional icon ⛱" />
          </div>
          <div>
            <label class="label">Description</label>
            <textarea v-model="form.description" rows="2" class="input resize-none" placeholder="Optional description" />
          </div>
          <div class="flex gap-3">
            <button type="button" @click="$emit('close')" class="btn-ghost flex-1">Cancel</button>
            <button type="submit" :disabled="loading" class="btn-primary flex-1">
              {{ loading ? 'Creating…' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  close: []
  created: [payload: { name: string; icon: string; description: string }]
}>()

const loading = ref(false)
const form = ref({ name: '', icon: '', description: '' })

async function submit() {
  loading.value = true
  try {
    emit('created', { ...form.value })
    form.value = { name: '', icon: '', description: '' }
  } finally {
    loading.value = false
  }
}
</script>