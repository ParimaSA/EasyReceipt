<template>
  <div class="min-h-full w-full flex flex-col justify-center items-center bg-black border border-white/10 rounded-2xl p-8">

    <div class="h-40 w-full flex items-center justify-center">
      <img src="@/assets/images/logo.png" alt="logo" class="h-full object-contain" />
    </div>

    <h1 class="text-3xl font-bold text-white mb-6 -mt-4">Welcome Back</h1>

    <form @submit.prevent="handleLogin" class="w-full space-y-4 text-white">
      <div>
        <label class="block text-xs font-semibold uppercase tracking-wider mb-1.5">Email</label>
        <input
          v-model="form.email" type="email" required
          class="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 placeholder:text-gray-400 placeholder:opacity-100 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400/50 transition-all"
          placeholder="you@example.com"
          style="color: white; --placeholder-color: #9ca3af;"
        />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase tracking-wider mb-1.5">Password</label>
        <input
          v-model="form.password" type="password" required
          class="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 placeholder:text-gray-400 placeholder:opacity-100 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400/50 transition-all"
          placeholder="••••••••"
        />
      </div>
      <p v-if="error" class="text-sm px-3 py-2 rounded-lg">{{ error }}</p>
      <button
        type="submit"
        :disabled="authStore.loading"
        class="w-full py-3 rounded-xl bg-amber-500 font-semibold hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2 cursor-pointer"
      >
        {{ authStore.loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <p class="text-center text-sm text-gray-300 mt-6">
      No account?
      <button @click="$emit('switch', 'login')" class="text-amber-400 hover:text-amber-300 font-medium">Create one</button>    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({ email: '', password: '' })
const error = ref('')
const emit = defineEmits(['switch'])

async function handleLogin() {
  error.value = ''
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? '⚠️ Login failed. Please try again.'
  }
}
</script>
