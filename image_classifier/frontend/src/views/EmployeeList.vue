<template>
  <div class="employee-list-container">
    <div class="employee-header">
      <h1>Сотрудники</h1>
      <button
        v-if="isAdmin"
        @click="goToEmployee('new')"
        class="btn-primary"
      >
        Добавить сотрудника
      </button>
    </div>

    <div v-if="!isAdmin && !loading" class="access-denied">
      У вас нет прав для просмотра сотрудников.
    </div>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="!employees.length" class="empty-message">Нет сотрудников</div>

    <!-- Карточки сотрудников -->
    <div v-else class="employee-grid">
      <div v-for="emp in employees" :key="emp.id" class="employee-card">
        <h2 class="emp-name">{{ emp.full_name }}</h2>
        <p class="emp-info"><strong>Должность:</strong> {{ emp.position }}</p>
        <p class="emp-info"><strong>Округ:</strong> {{ getDistrictName(emp.district) }}</p>
        <p class="emp-info"><strong>Район:</strong> {{ getRegionName(emp.region) }}</p>

        <div class="card-actions">
          <button @click="goToEmployee(emp.id)" class="btn-warning">Редактировать</button>
          <button @click="deleteEmployee(emp.id)" class="btn-danger">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'


const backendUrl = '/api'
const employees = ref([])
const districts = ref([])
const regions = ref([])
const loading = ref(true)
const router = useRouter()
const isAdmin = ref(false)

const fetchMeta = async () => {
  const [dRes, rRes] = await Promise.all([
    axios.get(`${backendUrl}/api/districts/`),
    axios.get(`${backendUrl}/api/regions/`)
  ])
  districts.value = dRes.data
  regions.value = rRes.data
}

const fetchEmployees = async () => {
  loading.value = true
  const { data } = await axios.get(`${backendUrl}/api/employees/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
  })
  employees.value = data
  loading.value = false
}

const getDistrictName = id => {
  return (districts.value.find(d => d.id === id) || {}).name || ''
}
const getRegionName = id => {
  return (regions.value.find(r => r.id === id) || {}).name || ''
}

const goToEmployee = id => {
  router.push({ name: 'EmployeeEdit', params: { id } })
}

const deleteEmployee = async id => {
  if (!confirm('Удалить сотрудника?')) return
  await axios.delete(`${backendUrl}/api/employees/${id}/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
  })
  fetchEmployees()
}

const fetchCurrentUser = async () => {
  const {data} = await axios.get(`${backendUrl}/api/me/`, {
    headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}
  })
  isAdmin.value = data.is_superuser
}

onMounted(async () => {
  await fetchCurrentUser()
  if (!isAdmin.value) {
    loading.value = false
    return
  }

  await fetchMeta()
  await fetchEmployees()
})

</script>

<style scoped>
.employee-list-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1rem;
  font-family: 'Inter', sans-serif;
}

.employee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.employee-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
}

.access-denied {
  text-align: center;
  color: #dc2626;
  font-weight: 500;
}

.loading,
.empty-message {
  text-align: center;
  color: #6b7280;
  margin-top: 2rem;
}

.employee-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 1.5rem;
}

.employee-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease;
}

.employee-card:hover {
  transform: translateY(-4px);
}

.emp-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.emp-info {
  font-size: 0.95rem;
  color: #374151;
  margin-bottom: 0.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: background 0.2s ease;
  border: none;
  cursor: pointer;
}
.btn-primary:hover {
  background: #1d4ed8;
}

.btn-warning {
  background: #f59e0b;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
}
.btn-warning:hover {
  background: #d97706;
}

.btn-danger {
  background: #ef4444;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
}
.btn-danger:hover {
  background: #dc2626;
}

</style>