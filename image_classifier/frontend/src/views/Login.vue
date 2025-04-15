<template>
  <div class="container">
    <h2>Вход</h2>
    <form @submit.prevent="login" class="form">
      <input v-model="username" placeholder="Имя пользователя" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <button type="submit">Войти</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  try {
    const response = await axios.post('/auth/login/', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('access', response.data.access)
    localStorage.setItem('refresh', response.data.refresh)
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
    router.push('/')
  } catch (err) {
    alert('Ошибка входа')
    console.error(err)
  }
}
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
input {
  padding: 8px;
}
button {
  padding: 10px;
  background-color: #2ecc71;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
