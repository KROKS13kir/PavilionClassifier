// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home            from '@/views/Home.vue'
import Login           from '@/views/Login.vue'
import Register        from '@/views/Register.vue'
import Cabinet       from '@/views/Cabinet.vue'
import PavilionCreate  from '@/views/PavilionCreate.vue'
import PavilionList    from '@/views/PavilionList.vue'
import PavilionEdit    from '@/views/PavilionEdit.vue'
import EmployeeList    from '@/views/EmployeeList.vue'
import EmployeeEdit    from '@/views/EmployeeEdit.vue'
import OrderList       from '@/views/OrderList.vue'
import OrderEdit       from '@/views/OrderEdit.vue'
import { useAuthStore } from '@/stores/auth'
import Dashboard from "@/views/Dashboard.vue";

const routes = [
  { path: '/',   name: 'Home',      component: Home },
  { path: '/login',  name: 'Login',     component: Login },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAdmin: true }
  },
  {
    path: '/cabinet',
    name: 'Cabinet',
    component: Cabinet,
    meta: { requiresAuth: true }
  },

  // Павильоны
  {
    path: '/pavilions/create',
    name: 'PavilionCreate',
    component: PavilionCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/pavilions',
    name: 'PavilionList',
    component: PavilionList,
    meta: { requiresAuth: true }
  },
  {
    path: '/pavilions/:id',
    name: 'PavilionEdit',
    component: PavilionEdit,
    props: true,
    meta: { requiresAuth: true }
  },

  // Сотрудники
  {
    path: '/employees',
    name: 'EmployeeList',
    component: EmployeeList,
    meta: { requiresAuth: true }
  },
  {
    path: '/employees/:id',
    name: 'EmployeeEdit',
    component: EmployeeEdit,
    props: true,
    meta: { requiresAuth: true }
  },

  // Наряды: отдельный маршрут для нового и для редактирования
  {
    path: '/orders',
    name: 'OrderList',
    component: OrderList,
    meta: {requiresAuth: true}
  },
  {
    path: '/orders/create',
    name: 'OrderCreate',         // <-- было OrderEdit
    component: OrderEdit,
    props: route => ({id: 'new'}),
    meta: {requiresAuth: true}
  },
  {
    path: '/orders/:id',
    name: 'OrderEdit',
    component: OrderEdit,
    props: route => ({id: route.params.id}),
    meta: {requiresAuth: true}
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Глобальный guard
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next({ name: 'Login' })
  }
  if (to.meta.requiresAdmin && (!auth.isLoggedIn || !auth.user?.isAdmin)) {
    return next({ name: 'Home' })
  }
  next()
})

export default router
