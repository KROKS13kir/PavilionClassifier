<template>
  <div class="profile-card">
    <h2 class="title">Личный кабинет</h2>
    <div v-if="user" class="profile-info">
      <p><strong>Логин:</strong> {{ user.username }}</p>
      <p><strong>ФИО:</strong> {{ user.full_name }}</p>
      <p><strong>Должность:</strong> {{ user.position || '—' }}</p>
      <p><strong>Округ:</strong> {{ user.district_name || '—' }}</p>
      <p><strong>Права:</strong> {{ user.is_superuser ? 'Администратор' : 'Сотрудник' }}</p>

      <button @click="logout" class="btn btn-red">Выйти</button>
    </div>
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
    const res = await axios.get('/me/', {
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
  delete axios.defaults.headers.common['Authorization']
  router.push('/login')
}
</script>

<style scoped>
.profile-card {
  max-width: 500px;
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

.profile-info p {
  margin: 0.5rem 0;
  font-size: 1rem;
}

.btn {
  padding: 0.75rem 1.25rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.5rem;
  text-align: center;
  border: none;
  cursor: pointer;
  margin-top: 1.5rem;
}

.btn-red {
  background-color: #ef4444;
  color: white;
}
.btn-red:hover {
  background-color: #dc2626;
}

</style>
