<template>
  <div class="dashboard">
    <h2>Личный кабинет</h2>
    <div v-if="user" class="info">
      <p><strong>Пользователь:</strong> {{ user.username }}</p>
      <p><strong>ФИО:</strong> {{ user.full_name }}</p>
      <p><strong>Должность:</strong> {{ user.position }}</p>
      <p><strong>Округ:</strong> {{ user.district }}</p>
      <p><strong>Права:</strong> {{ user.is_premium ? 'Администратор' : 'Обычный пользователь' }}</p>
      <button @click="logout">Выйти</button>
    </div>
    <router-link to="/upload">
  <button>Загрузить изображения</button>
</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const user = ref(null)
const router = useRouter()

onMounted(async () => {
  try {
    const res = await axios.get('/auth/user/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access')}`
      }
    })
    user.value = res.data
  } catch (err) {
    router.push('/login')
  }
})

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  axios.defaults.headers.common['Authorization'] = ''
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  max-width: 500px;
  margin: auto;
  padding: 20px;
}
.info p {
  margin: 8px 0;
}
button {
  margin-top: 15px;
  padding: 10px;
  background-color: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
