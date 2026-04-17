import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { title: '法务咨询' }
    },
    {
      path: '/survey',
      name: 'survey',
      component: () => import('@/views/Survey.vue'),
      meta: { title: '企业调查表' }
    },
    {
      path: '/contract',
      name: 'contract',
      component: () => import('@/views/Contract.vue'),
      meta: { title: '合同诊断' }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: () => import('@/views/Knowledge.vue'),
      meta: { title: '知识库' }
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/History.vue'),
      meta: { title: '咨询历史' }
    }
  ]
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI 法律咨询系统`
  }
  next()
})

export default router