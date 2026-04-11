<template>
  <div class="flex h-screen bg-[var(--color-bg)] overflow-hidden">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-40 flex flex-col bg-black text-white transition-all duration-300',
        sidebarOpen ? 'w-60' : 'w-16',
        'lg:relative lg:translate-x-0',
        !sidebarOpen && '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 py-5 border-b border-gray-300">
        <div class="w-8 h-8 rounded-lg bg-amber-400 flex items-center justify-center flex-shrink-0">
          <span class="font-bold text-sm">ER</span>
        </div>
        <Transition name="fade">
          <span v-if="sidebarOpen" class="font-display font-semibold text-lg tracking-tight">
            EasyReceipt
          </span>
        </Transition>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 space-y-1 px-2 overflow-y-auto">
        <NavItem :to="{ name: 'Dashboard' }" :icon="HomeIcon" label="Dashboard" :collapsed="!sidebarOpen" />
        <NavItem :to="{ name: 'Records' }" :icon="DocumentTextIcon" label="My Records" :collapsed="!sidebarOpen" />
        <NavItem :to="{ name: 'Groups' }" :icon="UserGroupIcon" label="Groups" :collapsed="!sidebarOpen" />

        <!-- Group sub-navigation -->
        <template v-if="groupsStore.groups.length && sidebarOpen">
          <div class="pt-2 pb-1 px-2">
            <p class="text-xs font-semibold text-ink-400 uppercase tracking-wider">My Groups</p>
          </div>
          <NavItem
            v-for="group in groupsStore.groups.slice(0, 5)"
            :key="group.id"
            :to="{ name: 'GroupDashboard', params: { id: group.id } }"
            :icon="FolderIcon"
            :label="group.name"
            :collapsed="false"
            small
          />
        </template>
      </nav>

      <!-- Profile -->
      <div class="border-t p-3">
        <div
          class="flex items-center gap-3 px-2 py-2 rounded-xl transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-amber-400 flex items-center justify-center flex-shrink-0">
            <span class="text-white font-bold text-xs">
              {{ authStore.user?.username?.[0]?.toUpperCase() ?? 'J' }}
            </span>
          </div>
          <Transition name="fade">
            <div v-if="sidebarOpen" class="min-w-0">
              <p class="font-medium truncate">{{ authStore.user?.username || "John Doe" }}</p>
            </div>
          </Transition>
        </div>
        <button
          v-if="sidebarOpen"
          @click="authStore.logout(); $router.push('/login')"
          class="mt-2 w-full flex items-center gap-2 px-2 py-2 rounded-xl text-ink-400 hover:text-white hover:bg-ink-700 transition-colors text-sm"
        >
          <ArrowRightOnRectangleIcon class="w-4 h-4" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top bar -->
      <header class="flex items-center gap-4 px-6 py-4 bg-white border-b border-slate-100 flex-shrink-0">
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="p-2 rounded-lg hover:bg-slate-100 transition-colors text-ink-600"
        >
          <Bars3Icon class="w-5 h-5" />
        </button>
        <div class="flex-1" />
        <span class="text-xs font-semibold text-ink-400 uppercase tracking-wider bg-ink-50 px-3 py-1 rounded-full">
          {{ authStore.user?.role }}
        </span>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView, RouterLink } from 'vue-router'
import {
  HomeIcon, DocumentTextIcon, UserGroupIcon, FolderIcon,
  Bars3Icon, ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import NavItem from '@/components/common/NavItem.vue'

const authStore = useAuthStore()
const groupsStore = useGroupsStore()
const sidebarOpen = ref(true)

onMounted(() => {
  groupsStore.mockGroups()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
