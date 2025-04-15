<template>
  <div class="container">
    <h2>Регистрация</h2>
    <form @submit.prevent="register" class="form">
      <input v-model="username" placeholder="Имя пользователя" required />
      <input v-model="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <input v-model="fullName" placeholder="ФИО" required />
      <input v-model="position" placeholder="Должность" required />
      <input v-model="district" placeholder="Округ" required />
      <button type="submit">Зарегистрироваться</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const email = ref('')
const password = ref('')
const fullName = ref('')
const position = ref('')
const district = ref('')
const router = useRouter()

const register = async () => {
  try {
    await axios.post('/auth/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      position: position.value,
      district: district.value,
    }, {
      headers: {
        Authorization: ''
      }
    })
    router.push('/login')
  } catch (err) {
    alert('Ошибка регистрации')
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
  background-color: #2e86de;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
