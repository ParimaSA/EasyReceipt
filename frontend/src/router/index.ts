import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
    },
    // paths after login
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: '/records',
          name: 'Records',
          component: () => import('@/views/records/RecordsView.vue'),
        },
        {
          path: '/groups',
          name: 'Groups',
          component: () => import('@/views/groups/GroupListView.vue'),
        },
        {
          path: '/groups/:id/dashboard',
          name: 'GroupDashboard',
          component: () => import('@/views/dashboard/GroupDashboardView.vue'),
        },
        {
          path: '/groups/:id',
          name: 'GroupDetail',
          component: () => import('@/views/groups/GroupDetailView.vue'),
        },
        {
          path: '/groups/:id/records',
          name: 'GroupRecords',
          component: () => import('@/views/records/GroupRecordsView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.user && localStorage.getItem('access_token')) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Home', query: { redirect: to.fullPath } }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'Dashboard' }
  }

  return true
})

export default router
