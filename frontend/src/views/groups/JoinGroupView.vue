<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="absolute top-1/3 left-1/2 w-80 h-80 bg-amber-400/10 rounded-full blur-3xl pointer-events-none -translate-x-1/2" />

    <div class="relative w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-amber-400 rounded-2xl mb-4 shadow-lg">
          <span class="text-white font-bold text-xl">ER</span>
        </div>
        <h1 class="text-3xl text-black font-bold">EasyReceipt</h1>
      </div>

      <div class="bg-black backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl text-center space-y-4">
        <!-- Loading -->
        <template v-if="status === 'loading'">
          <div class="w-12 h-12 rounded-full border-4 border-amber-400/30 border-t-amber-400 animate-spin mx-auto" />
          <p class="text-white font-medium">Joining group…</p>
        </template>

        <!-- Success -->
        <template v-else-if="status === 'success'">
          <div class="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto">
            <CheckIcon class="w-8 h-8 text-amber-400 text-bold" />
          </div>
          <h2 class="text-xl text-bold text-white">You're in!</h2>
          <p class="text-white text-sm">You joined <strong class="text-white">{{ groupName }}</strong></p>
          <button @click="router.push('/groups')" class="w-full py-3 rounded-xl bg-amber-400 font-semibold text-sm hover:bg-amber-300 transition-colors">
            Go to Groups
          </button>
        </template>

        <!-- Need to login first -->
        <template v-else-if="status === 'unauthenticated'">
          <div class="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto">
            <UserIcon class="w-8 h-8 text-amber-400" />
          </div>
          <h2 class="text-xl font-bold text-white">Sign in to join</h2>
          <p class="text-white text-sm">You need an account to accept this invitation.</p>
          <div class="space-y-2">
            <RouterLink
              :to="{ name: 'Home', query: { redirect: route.fullPath } }"
              class="block w-full py-3 rounded-xl bg-amber-400 font-semibold text-sm hover:bg-amber-300 transition-colors"
            >
              Sign in / Create account
            </RouterLink>
          </div>
        </template>

        <!-- Error -->
        <template v-else-if="status === 'error'">
          <div class="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto">
            <XCircleIcon class="w-8 h-8 text-coral-400" />
          </div>
          <h2 class="text-xl text-white font-bold">Invitation Error</h2>
          <p class="text-white text-sm">{{ errorMsg }}</p>
          <RouterLink to="/groups" class="block w-full py-3 rounded-xl bg-white/30 text-white font-semibold text-sm hover:bg-white/20 transition-colors">
            Back to Groups
          </RouterLink>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { CheckIcon, UserIcon, XCircleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const groupsStore = useGroupsStore()

const status = ref<'loading' | 'success' | 'error' | 'unauthenticated'>('loading')
const groupName = ref('')
const errorMsg = ref('')

onMounted(async () => {
  const token = route.params.token as string

  if (!authStore.isAuthenticated) {
    // Try restoring session first
    if (localStorage.getItem('access_token')) {
      await authStore.fetchMe()
    }
    if (!authStore.isAuthenticated) {
      status.value = 'unauthenticated'
      return
    }
  }

  try {
    const group = await groupsStore.joinGroup(token)
    groupName.value = group.name
    status.value = 'success'
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail ?? 'Invalid or expired invitation link.'
    status.value = 'error'
  }
})
</script>
