<template>
  <div class="container">
    <h1>Добро пожаловать 👋</h1>
    <p>Это приложение для классификации изображений.</p>
    <router-link v-if="!isLoggedIn" to="/login"><button>Войти</button></router-link>
    <router-link v-if="!isLoggedIn" to="/register"><button>Регистрация</button></router-link>
    <router-link v-if="isLoggedIn" to="/dashboard"><button>Личный кабинет</button></router-link>
    <router-link to="/upload"><button>Классификация изображений</button></router-link>
  </div>
</template>

<script setup>
const isLoggedIn = localStorage.getItem('access') !== null
</script>

<style scoped>
.container {
  text-align: center;
  padding: 30px;
}
button {
  margin: 10px;
  padding: 10px 15px;
}
</style>
