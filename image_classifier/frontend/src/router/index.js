import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import ImageClassifier from '../views/ImageClassifier.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/upload', name: 'ImageClassifier', component: ImageClassifier }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
