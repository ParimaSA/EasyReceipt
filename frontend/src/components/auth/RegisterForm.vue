<template>
  <div class="h-full w-full flex flex-col justify-center items-center bg-black border border-white/10 rounded-2xl p-8">

    <div class="h-40 w-full flex items-center justify-center">
      <img src="@/assets/images/logo.png" alt="logo" class="h-full object-contain" />
    </div>

    <h1 class="text-3xl font-bold text-white mb-6 -mt-4">Get Started</h1>

    <form @submit.prevent="handleRegister" class="w-full space-y-4 text-white overflow-y-auto">
      <div>
        <label class="block text-xs font-semibold text-ink-300 uppercase tracking-wider mb-1.5">Username</label>
        <input
          v-model="form.username" required minlength="3"
          class="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-amber-400/50 transition-all"
          placeholder="jdoe"
        />
      </div>
      <div>
        <label class="block text-xs font-semibold text-ink-300 uppercase tracking-wider mb-1.5">Email</label>
        <input
          v-model="form.email" type="email" required
          class="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-amber-400/50 transition-all"
          placeholder="you@example.com"
        />
      </div>
      <div>
        <label class="block text-xs font-semibold text-ink-300 uppercase tracking-wider mb-1.5">Password</label>
        <input
          v-model="form.password" type="password" required minlength="8"
          class="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-amber-400/50 transition-all"
          placeholder="Min 8 characters"
        />
      </div>

      <p v-if="error" class="px-3 py-2 rounded-lg">{{ error }}</p>

      <button
        type="submit" :disabled="authStore.loading"
        class="w-full py-3 rounded-xl bg-amber-500 font-semibold hover:bg-amber-400 transition-colors disabled:opacity-50 mt-2"
      >
        {{ authStore.loading ? 'Creating account…' : 'Create account' }}
      </button>
    </form>

    <p class="text-center text-sm text-white mt-6">
      Already have an account?
      <button @click="$emit('switch', 'login')" class="text-amber-400 hover:text-amber-300 font-medium">Sign in</button>
    </p>
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({ email: '', username: '', password: '' })
const error = ref('')
const emit = defineEmits(['switch'])

async function handleRegister() {
  error.value = ''
  try {
    await authStore.register(form.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Registration failed.'
  }
}
</script>
