<template>
  <nav class="navbar">
    <router-link to="/">🏠 Главная</router-link>
    <router-link to="/upload">🖼 Классификация</router-link>
    <router-link v-if="!isLoggedIn" to="/login">🔑 Войти</router-link>
    <router-link v-if="!isLoggedIn" to="/register">📝 Регистрация</router-link>
    <router-link v-if="isLoggedIn" to="/dashboard">👤 Кабинет</router-link>
    <a v-if="isLoggedIn" @click="logout" href="#">🚪 Выйти</a>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = localStorage.getItem('access') !== null

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  gap: 20px;
  padding: 15px;
  background: #f1f1f1;
}
a {
  cursor: pointer;
}
</style>
