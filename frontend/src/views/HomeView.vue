<template>
  <div class="h-screen flex items-center justify-center px-[18vw] py-[16vh] gap-x-12">
    <div class="h-full w-full bg-[#ffaf45] rounded-2xl overflow-hidden hidden md:block flex items-center justify-center p-2">
      <img src="@/assets/images/poster.png" alt="poster" class="h-full w-full object-contain" />
    </div>

    <div class="h-full w-full">
      <LoginForm v-if="view === 'login'" @switch="view = 'register'" />
      <RegisterForm v-else @switch="view = 'login'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginForm from '@/components/auth/LoginForm.vue';
import RegisterForm from '@/components/auth/RegisterForm.vue';

const view = ref('login')

</script>
