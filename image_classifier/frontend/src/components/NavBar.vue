<template>
  <nav class="navbar">
    <router-link to="/" class="nav-item">
      <fa icon="home" /> Главная
    </router-link>
    <router-link v-if="!auth.isLoggedIn" to="/login" class="nav-item">
      <fa icon="sign-in-alt" /> Войти
    </router-link>
    <router-link
      v-if="auth.isLoggedIn && auth.user?.isAdmin"
      to="/register"
      class="nav-item"
    >
      <fa icon="user-plus" /> Регистрация
    </router-link>
    <router-link v-if="auth.isLoggedIn" to="/cabinet" class="nav-item">
      <fa icon="user-circle" /> Кабинет
    </router-link>
    <router-link v-if="auth.isLoggedIn" to="/pavilions" class="nav-item">
      <fa icon="building-columns" /> Павильоны
    </router-link>
    <router-link v-if="auth.isLoggedIn" to="/employees" class="nav-item">
      <fa icon="users" /> Сотрудники
    </router-link>
    <router-link v-if="auth.isLoggedIn" to="/orders" class="nav-item">
      <fa icon="clipboard-list" /> Наряды
    </router-link>
    <router-link v-if="auth.isLoggedIn" to="/dashboard" class="nav-item">
      <fa icon="chart-line"/>
      Дашборд
    </router-link>
    <a v-if="auth.isLoggedIn" @click.prevent="logout" class="nav-item logout">
      <fa icon="sign-out-alt" /> Выйти
    </a>
  </nav>
</template>


<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  align-items: center;
  border-radius: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  font-weight: 500;
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}
.nav-item:hover {
  background: #edf2f7;
  color: #2d3748;
}
.nav-item.active {
  background: #2b6cb0;
  color: #fff;
}
.logout {
  margin-left: auto;
  color: #e53e3e;
}
.logout:hover {
  background: #fed7d7;
  color: #c53030;
}
</style>
