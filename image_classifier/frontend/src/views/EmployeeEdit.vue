<template>
  <div class="employee-edit-card">
    <h1 class="title">
      {{ isNew ? 'Добавить сотрудника' : 'Редактировать сотрудника' }}
    </h1>

    <div v-if="loading" class="loading-text">Загрузка...</div>

    <form v-else @submit.prevent="saveEmployee" class="form-grid">
      <div class="form-group">
        <label>Логин (username)</label>
        <input v-model="employee.username" required />
      </div>

      <div class="form-group">
        <label>Пароль</label>
        <input v-model="employee.password" type="password" :required="isNew" />
        <small v-if="!isNew">Оставьте пустым, чтобы не менять пароль</small>
      </div>

      <div class="form-group">
        <label>Email</label>
        <input v-model="employee.email" type="email" />
      </div>

      <div class="form-group">
        <label>ФИО</label>
        <input v-model="employee.full_name" required />
      </div>

      <div class="form-group">
        <label>Токен для входа в Телеграм</label>
        <input v-model="employee.telegram_token" />
      </div>

      <div class="form-group">
        <label>Должность</label>
        <input v-model="employee.position" required />
      </div>

      <div class="form-group">
        <label>Округ</label>
        <select v-model="employee.district" required>
          <option disabled value="">-- Выберите --</option>
          <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>

      <div class="form-group">
        <label>Район</label>
        <select v-model="employee.region">
          <option value="">-- Все --</option>
          <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
      </div>

      <div class="checkbox-group">
        <label><input type="checkbox" v-model="employee.is_staff" /> Доступ в админку</label>
        <label><input type="checkbox" v-model="employee.is_superuser" /> Администратор</label>
        <label><input type="checkbox" v-model="employee.is_active" /> Активный пользователь</label>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-green">Сохранить</button>
        <router-link to="/employees" class="btn btn-gray">Отмена</router-link>
        <button
          v-if="!isNew"
          type="button"
          @click="deleteEmployee"
          class="btn btn-red ml-auto"
        >
          Удалить
        </button>
      </div>
    </form>
  </div>
</template>


<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const id = ref(route.params.id)
const isNew = ref(id.value === 'new')

const employee = ref({
  username: '',
  email: '',
  password: '', // только при создании
  full_name: '',
  position: '',
  district: null,
  region: null,
  telegram_chat_id: '',
  telegram_token: '',
  is_staff: false,
  is_superuser: false,
  is_active: true
})

const districts = ref([])
const regions = ref([])
const loading = ref(true)

const fetchMeta = async () => {
  const [dRes, rRes] = await Promise.all([
    axios.get(`districts/`),
    axios.get(`regions/`)
  ])
  districts.value = dRes.data
  regions.value   = rRes.data
}

const fetchEmployee = async () => {
  if (isNew.value) {
    loading.value = false
    return
  }
  const { data } = await axios.get(`employees/${id.value}/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
  })
  employee.value = data
  loading.value = false
}

const saveEmployee = async () => {
  const headers = {Authorization: `Bearer ${localStorage.getItem('access')}`}
  const dataToSend = {...employee.value}

  if (!dataToSend.password) {
    delete dataToSend.password
  }
  if (!dataToSend.telegram_chat_id) {
    delete dataToSend.telegram_chat_id
  }

  if (isNew.value) {
    await axios.post(`employees/`, dataToSend, {headers})
  } else {
    await axios.put(`employees/${id.value}/`, dataToSend, {headers})
  }
  router.push({name: 'EmployeeList'})
}


const deleteEmployee = async () => {
  if (!confirm('Удалить сотрудника?')) return
  await axios.delete(`employees/${id.value}/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
  })
  router.push({ name: 'Employees' })
}

watch(
  () => route.params.id,
  newId => {
    id.value = newId
    isNew.value = newId === 'new'
    loading.value = true
    fetchEmployee()
  }
)

onMounted(async () => {
  await fetchMeta()
  await fetchEmployee()
})
</script>

<style scoped>
.employee-edit-card {
  max-width: 650px;
  margin: 2rem auto;
  background: #ffffff;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  font-family: 'Inter', sans-serif;
  color: #1f2937;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
}

.loading-text {
  text-align: center;
  color: #6b7280;
  font-size: 1rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.form-group small {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 0.5rem;
  font-size: 0.95rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 0.375rem;
  text-decoration: none;
  text-align: center;
  transition: background 0.2s;
  cursor: pointer;
  border: none;
}

.btn-green {
  background: #10b981;
  color: white;
}
.btn-green:hover {
  background: #059669;
}

.btn-gray {
  background: #e5e7eb;
  color: #111827;
}
.btn-gray:hover {
  background: #d1d5db;
}

.btn-red {
  background: #ef4444;
  color: white;
}
.btn-red:hover {
  background: #dc2626;
}

</style>