import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import ImageClassifier from '../views/ImageClassifier.vue'
import PavilionList from "../views/PavilionList.vue";
import PavilionEdit from "../views/PavilionEdit.vue";

const routes = [
  {path: '/', component: Home},
  {path: '/login', component: Login},
  {path: '/register', component: Register},
  {path: '/dashboard', component: Dashboard},
  {path: '/upload', component: ImageClassifier},
  {path: '/pavilions', name: 'Pavilions', component: PavilionList},
  { path: '/pavilions/:id', name: 'PavilionEdit', component: PavilionEdit },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
