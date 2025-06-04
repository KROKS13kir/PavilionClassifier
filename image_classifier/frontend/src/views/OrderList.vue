<template>
  <div class="orders-container">
    <div class="orders-header">
      <h1>Наряды на ремонт</h1>
      <button v-if="isAdmin" @click="createOrder" class="btn-primary">Добавить наряд</button>
    </div>

    <div class="filters">
      <select v-model="filters.employee" class="filter-input">
        <option value="">Все сотрудники</option>
        <option v-for="e in employees" :key="e.id" :value="e.id">{{ e.full_name }}</option>
      </select>

      <select v-model="filters.status" class="filter-input">
        <option value="">Все статусы</option>
        <option value="new">Новый</option>
        <option value="assigned">Назначен</option>
        <option value="in_progress">В работе</option>
        <option value="done">Выполнен</option>
      </select>

      <input type="date" v-model="filters.date" class="filter-input" />

      <button @click="clearFilters" class="btn-secondary">Сбросить фильтры</button>
    </div>

    <table v-if="!loading && filteredOrders.length" class="orders-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Павильон</th>
          <th>Сотрудник</th>
          <th @click="toggleDateSort" class="sortable">
            Дата
            <span>{{ sortAsc ? '▲' : '▼' }}</span>
          </th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in sortedOrders" :key="order.id">
          <td>{{ order.id }}</td>
          <td>{{ getPavilionName(order.pavilion) }}</td>
          <td>{{ getEmployeeName(order.employee) }}</td>
          <td>{{ formatDate(order.scheduled_for) }}</td>
          <td>{{ statusLabels[order.status] }}</td>
          <td class="px-4 py-2 border">
            <div class="actions-cell">
              <button @click="viewOrder(order.id)" class="btn-neutral">Просмотр</button>
              <button v-if="isAdmin" @click="editOrder(order.id)" class="btn-edit">Редактировать</button>
              <button v-if="isAdmin" @click="deleteOrder(order.id)" class="btn-delete">Удалить</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-message">Нет подходящих нарядов</div>
    <div v-if="loading" class="loading-message">Загрузка...</div>
  </div>
</template>


<script setup>
// Импортируем нужные функции и библиотеки
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'


// Vue Router
const router = useRouter()

// Состояние компонента
const orders    = ref([])
const pavilions = ref([])
const employees = ref([])
const loading   = ref(true)
const isAdmin   = ref(false)

// Отображаемые метки статусов
const statusLabels = {
  new:        'Новый',
  assigned:   'Назначен',
  in_progress:'В работе',
  done:       'Выполнен'
}
/**
 * Получаем данные текущего пользователя,
 * чтобы узнать, является ли он админом
 */
const fetchCurrentUser = async () => {
  try {
    const { data } = await axios.get(`me/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    isAdmin.value = data.is_superuser
  } catch (e) {
    console.error('Не удалось получить данные пользователя', e)
  }
}

/**
 * Фетчим справочники павильонов и сотрудников
 */
const fetchMeta = async () => {
  try {
    const [pRes, eRes] = await Promise.all([
      axios.get(`pavilions/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
      }),
      axios.get(`employees/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
      })
    ])
    pavilions.value = pRes.data
    employees.value = eRes.data
  } catch (e) {
    console.error('Не удалось получить справочники', e)
  }
}

/**
 * Загружаем список нарядов
 */
const fetchOrders = async () => {
  loading.value = true
  try {
    const { data } = await axios.get(`repair-orders/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    orders.value = data
  } catch (e) {
    console.error('Не удалось получить наряды', e)
  } finally {
    loading.value = false
  }
}

/**
 * Вспомогательные функции для отображения
 */
const getPavilionName = id => {
  const p = pavilions.value.find(x => x.id === id)
  return p ? `${p.stop_name} (${p.mpv_code})` : id
}
const getEmployeeName = emp => emp?.full_name || ''
const formatDate = d => d ? new Date(d).toLocaleDateString('ru-RU') : ''

/**
 * Переход на создание нового наряда
 */
const createOrder = () => {
  router.push({ name: 'OrderCreate' })
}

/**
 * Переход на редактирование существующего наряда
 */
const viewOrder = id => {
  router.push({ name: 'OrderEdit', params: { id: String(id) }, query: { readonly: 'true' } })
}

const editOrder = id => {
  router.push({ name: 'OrderEdit', params: { id: String(id) } }) // без query
}
/**
 * Удаление наряда
 */
const deleteOrder = async id => {
  if (!confirm('Удалить наряд?')) return
  try {
    await axios.delete(`repair-orders/${id}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    await fetchOrders()
  } catch (e) {
    console.error('Ошибка при удалении наряда', e)
  }
}

// При монтировании компонента загружаем всё необходимое
onMounted(async () => {
  await fetchCurrentUser()
  await fetchMeta()
  await fetchOrders()
  // Можно обновлять список раз в 2 минуты
  setInterval(fetchOrders, 120000)
})

const filters = ref({
  employee: '',
  status: '',
  date: ''
})
const sortAsc = ref(true)

const clearFilters = () => {
  filters.value = { employee: '', status: '', date: '' }
}

const filteredOrders = computed(() => {
  return orders.value.filter(order => {
    const matchEmployee = !filters.value.employee || order.employee?.id === +filters.value.employee
    const matchStatus = !filters.value.status || order.status === filters.value.status
    const matchDate = !filters.value.date || order.scheduled_for.startsWith(filters.value.date)
    return matchEmployee && matchStatus && matchDate
  })
})

const sortedOrders = computed(() => {
  return [...filteredOrders.value].sort((a, b) => {
    const dateA = new Date(a.scheduled_for)
    const dateB = new Date(b.scheduled_for)
    return sortAsc.value ? dateA - dateB : dateB - dateA
  })
})

const toggleDateSort = () => {
  sortAsc.value = !sortAsc.value
}
</script>


<style scoped>
.orders-container {
  max-width: 1100px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
}

.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.9rem;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th,
.orders-table td {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
}

.orders-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.loading-message,
.empty-message {
  text-align: center;
  color: #6b7280;
  margin-top: 2rem;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #111827;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn-neutral {
  background-color: #6b7280;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}
.btn-edit {
  background-color: #f59e0b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}
.btn-delete {
  background-color: #ef4444;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}
.btn-neutral:hover { background-color: #4b5563; }
.btn-edit:hover    { background-color: #d97706; }
.btn-delete:hover  { background-color: #b91c1c; }

.actions-cell {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
