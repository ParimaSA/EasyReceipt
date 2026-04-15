<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-70 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl p-6 space-y-4">
        <h3 class="text-xl font-semibold">{{ title }}</h3>
        <p class="text-sm" v-html="message" />
        <div class="flex gap-3 pt-1">
          <button @click="$emit('cancel')" class="btn-ghost flex-1">Cancel</button>
          <button @click="$emit('confirm')" class="btn-danger flex-1">Delete</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{ title: string; message: string }>()
defineEmits<{ confirm: []; cancel: [] }>()
</script>
