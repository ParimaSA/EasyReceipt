<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl p-6 space-y-4">
        <h3 class="font-display text-lg font-semibold">Create Invite Link</h3>
        <div>
          <label class="label">Invite As</label>
          <select v-model="form.invited_role" class="input">
            <option value="member">Member (can record)</option>
            <option value="viewer">Viewer (read-only)</option>
          </select>
        </div>
        <div>
          <label class="label">Max Uses (optional)</label>
          <input v-model.number="form.max_uses" type="number" min="1" class="input" placeholder="Unlimited" />
        </div>
        <div>
          <label class="label">Expires In (hours, optional)</label>
          <input v-model.number="form.expires_hours" type="number" min="1" class="input" placeholder="Never" />
        </div>
        <div class="flex gap-3">
          <button @click="$emit('close')" class="btn-ghost flex-1">Cancel</button>
          <button @click="$emit('submit', form)" :disabled="loading" class="btn-primary flex-1">
            {{ loading ? 'Creating…' : 'Create Link' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ loading: boolean }>()

defineEmits<{
  close: []
  submit: [form: { invited_role: 'member' | 'viewer', max_uses?: number, expires_hours?: number }]
}>()

const form = ref({
  invited_role: 'member' as 'member' | 'viewer',
  max_uses: undefined as number | undefined,
  expires_hours: undefined as number | undefined,
})
</script>