<template>
  <div class="card p-5">
    <h2 class="font-semibold mb-4">Invite Links</h2>
    <div v-if="invitations.length" class="space-y-3">
      <div
        v-for="inv in invitations" :key="inv.id"
        class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span :class="['badge', inv.invited_role === 'member' ? 'badge-member' : 'badge-viewer']">
              {{ inv.invited_role }}
            </span>
            <span :class="['text-xs font-medium', inv.is_active ? 'text-green-600' : 'text-gray-400']">
              {{ inv.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span class="text-xs">{{ inv.use_count }}{{ inv.max_uses ? `/${inv.max_uses}` : '' }} uses</span>
          </div>
          <p class="font-mono text-xs truncate">{{ inv.invite_url || `…/join/${inv.token}` }}</p>
        </div>
        <button @click="$emit('copy', inv)" class="p-2 rounded-lg hover:bg-white text-gray-400 hover:text-gray-700">
          <ClipboardDocumentIcon class="w-4 h-4" />
        </button>
        <button @click="$emit('revoke', inv.id)" class="p-2 rounded-lg hover:bg-coral-50 text-gray-400 hover:text-coral-500 transition-colors">
          <XCircleIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
    <p v-else class="text-sm text-gray-300">No invite links yet.</p>
  </div>
</template>

<script setup lang="ts">
import { ClipboardDocumentIcon, XCircleIcon } from '@heroicons/vue/24/outline'
import type { Invitation } from '@/types'

defineProps<{ invitations: Invitation[] }>()

defineEmits<{
  copy: [inv: Invitation]
  revoke: [id: string]
}>()
</script>