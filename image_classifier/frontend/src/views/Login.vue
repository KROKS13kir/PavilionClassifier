<template>
  <div class="login-card">
    <h2 class="title">Вход в систему</h2>
    <form @submit.prevent="login" class="login-form">
      <input
        v-model="username"
        placeholder="Имя пользователя"
        required
        class="input"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Пароль"
        required
        class="input"
      />
      <button type="submit" class="btn btn-green">Войти</button>
    </form>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'    // <- импорт стора

const username = ref('')
const password = ref('')
const router   = useRouter()
const auth     = useAuthStore()                // <- инициализируем стор

const login = async () => {
  try {
    const { data } = await axios.post('/auth/login/', {
      username: username.value,
      password: password.value,
    })

    // 1) Обновляем Pinia‐store
    auth.login(data.access)

    // 2) Если хотите, можно сохранить и refresh
    localStorage.setItem('refresh', data.refresh)

    // 3) Перенаправляем
    router.push('/')
  } catch (err) {
    alert('Ошибка входа')
    console.error(err)
  }
}
</script>

<style scoped>
.login-card {
  max-width: 420px;
  margin: 4rem auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  font-family: 'Inter', sans-serif;
  color: #1f2937;
  text-align: center;
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.btn {
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-green {
  background-color: #10b981;
  color: white;
}
.btn-green:hover {
  background-color: #059669;
}

</style>
