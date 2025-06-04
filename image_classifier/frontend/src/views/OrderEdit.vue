<template>
  <div class="order-edit-container">
    <h1 class="page-title">
      {{ isCreateMode ? 'Создать наряд' : canEdit ? 'Редактировать наряд' : 'Просмотр наряда' }}
    </h1>

    <div v-if="loading" class="loading">Загрузка...</div>

    <form v-else @submit.prevent="saveOrder" class="order-form">
      <!-- Павильон -->
      <div class="form-group">
        <label>Павильон</label>
        <template v-if="isCreateMode">
          <select v-model="order.pavilion" :disabled="!canEdit" required>
            <option disabled value="">-- Выберите павильон --</option>
            <option v-for="p in filteredPavilions" :key="p.id" :value="p.id">
              {{ p.stop_name }} ({{ p.mpv_code }})
            </option>
          </select>
        </template>
        <div v-else class="readonly-block">
          {{ selectedPavilion?.stop_name }} ({{ selectedPavilion?.mpv_code }})
        </div>
      </div>

      <!-- Изображения -->
      <div class="form-group">
        <label>Выберите изображения</label>
        <div v-if="isCreateMode && availableImages.length" class="image-carousel">
          <div v-for="img in availableImages" :key="img.id" class="image-card">
            <div class="carousel">
              <img :src="img.image_url" class="carousel-img"/>
            </div>
            <p class="carousel-caption">
              {{ img.confirmed_state || img.predicted_class }}
            </p>
            <label class="carousel-checkbox">
              <input type="checkbox" :value="img.id" v-model="selectedImageIds"/> Выбрать
            </label>
          </div>
        </div>
        <div v-else-if="!isCreateMode && orderImages.length" class="image-carousel">
          <div v-for="img in orderImages" :key="img.id" class="image-card">
            <img :src="img.image_url" class="image-thumb"/>
            <p class="image-info">{{ img.confirmed_state || img.predicted_class }}</p>
          </div>
        </div>
      </div>

      <!-- Инфо о павильоне -->
      <div v-if="selectedPavilion" class="pavilion-info">
        <p><strong>Улица:</strong> {{ selectedPavilion.street }}</p>
        <p><strong>Район:</strong> {{ selectedPavilion.region_name }}</p>
        <p><strong>Округ:</strong> {{ selectedPavilion.district_name }}</p>
        <p><strong>Номер павильона:</strong> {{ selectedPavilion.pavilion_number }}</p>
        <p><strong>Категория:</strong> {{ selectedPavilion.category }}</p>
        <p><strong>Адрес:</strong> {{ selectedPavilion.address }}</p>
      </div>

      <!-- Сотрудник -->
      <div class="form-group">
        <label>Сотрудник</label>
        <select v-model="order.employee_id" :disabled="!canEdit" required>
          <option disabled value="">-- Выберите сотрудника --</option>
          <option v-for="e in filteredEmployees" :key="e.id" :value="e.id">
            {{ e.full_name }} ({{ e.position }})
          </option>
        </select>
      </div>

      <!-- Дата выезда -->
      <div class="form-group">
        <label>Дата выезда</label>
        <input type="date" v-model="order.scheduled_for" :disabled="!canEdit" required/>
        <p v-if="order.scheduled_for" class="helper-text">
          Нагрузка: <strong>{{ workload }}</strong> наряд{{ workload !== 1 ? 'ов' : '' }}
        </p>
      </div>

      <!-- Срок исполнения -->
      <div class="form-group">
        <label>Срок исполнения</label>
        <input type="date" v-model="order.deadline" :disabled="!canEdit"/>
      </div>

      <!-- Статус -->
      <div class="form-group">
        <label>Статус</label>
        <select v-model="order.status" :disabled="!canEdit" required>
          <option v-for="(label, key) in statusLabels" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>

      <!-- Описание -->
      <div class="form-group">
        <label>Описание</label>
        <textarea v-model="order.description" rows="3" :readonly="!canEdit"></textarea>
      </div>

      <!-- Приоритет -->
      <div class="form-group">
        <label>Приоритет</label>
        <select v-model="order.priority" :disabled="!canEdit" required>
          <option v-for="(label, key) in priorityLabels" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>

      <!-- Дата выполнения -->
      <div v-if="order.completed_at" class="form-group">
        <label>Дата выполнения</label>
        <input type="text" :value="new Date(order.completed_at).toLocaleDateString('ru-RU')" readonly
               class="readonly-block"/>
      </div>

      <!-- Кнопки -->
      <div class="form-actions">
        <button v-if="canEdit" type="submit" class="btn btn-green">Сохранить</button>
        <router-link to="/orders" class="btn btn-gray">Назад</router-link>
        <button v-if="!isCreateMode && canEdit" type="button" @click="deleteOrder" class="btn btn-red ml-auto">
          Удалить
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import {ref, computed, watch, onMounted} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import axios from 'axios'


const router = useRouter()
const route = useRoute()

const props = defineProps({
  id: {type: String, default: 'new'},
  isNew: {type: Boolean, default: false}
})

const isCreateMode = computed(() => props.isNew || props.id === 'new')
const canEdit = computed(() => isAdmin.value && route.query.readonly !== 'true')

const loading = ref(true)
const isAdmin = ref(false)
const order = ref({
  pavilion: null,
  employee_id: null,
  scheduled_for: '',
  deadline: '',
  status: 'new',
  description: '',
  priority: 'medium'
})
const pavilions = ref([])
const employees = ref([])
const ordersList = ref([])
const availableImages = ref([])
const orderImages = ref([])
const selectedImageIds = ref([])

const statusLabels = {new: 'Новый', assigned: 'Назначен', in_progress: 'В работе', done: 'Выполнен'}
const priorityLabels = {low: 'Низкий', medium: 'Средний', high: 'Высокий'}

async function fetchCurrentUser() {
  try {
    const {data} = await axios.get(`me/`, {headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}})
    isAdmin.value = data.is_superuser
  } catch {
    isAdmin.value = false
  }
}

async function fetchMeta() {
  loading.value = true
  try {
    const [pRes, eRes, oRes] = await Promise.all([
      axios.get(`pavilions/`, {headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}}),
      axios.get(`employees/`, {headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}}),
      axios.get(`repair-orders/`, {headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}})
    ])
    pavilions.value = pRes.data
    employees.value = eRes.data
    ordersList.value = oRes.data
  } catch (e) {
    console.error('Ошибка meta:', e)
  } finally {
    loading.value = false
  }
}

async function fetchOrder() {
  if (isCreateMode.value) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const {data} = await axios.get(`repair-orders/${props.id}/`, {
      headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}
    })
    order.value = {
      pavilion: data.pavilion,
      employee_id: data.employee?.id || null,
      scheduled_for: data.scheduled_for,
      deadline: data.deadline,
      status: data.status,
      description: data.description || '',
      priority: data.priority || 'medium'
    }
    orderImages.value = data.images || []
    selectedImageIds.value = orderImages.value.map(i => i.id)
  } catch (e) {
    console.error('Ошибка fetchOrder:', e)
  } finally {
    loading.value = false
  }
}

async function saveOrder() {
  const headers = {Authorization: `Bearer ${localStorage.getItem('access')}`}
  if (order.value.employee_id && order.value.status === 'new') {
    order.value.status = 'assigned'
  }
  if (isCreateMode.value) {
    order.value.image_ids = selectedImageIds.value
  }
  try {
    const response = isCreateMode.value
        ? await axios.post(`repair-orders/`, order.value, {headers})
        : await axios.patch(`repair-orders/${props.id}/`, order.value, {headers})
    const finalStatus = response.data.status
    if (finalStatus === 'done') {
      await axios.patch(`pavilions/${order.value.pavilion}/`, {requires_repair: false}, {headers})
    }
    router.push({name: 'OrderList'})
  } catch (e) {
    console.error('Ошибка saveOrder:', e)
  }
}

async function deleteOrder() {
  if (!confirm('Удалить наряд?')) return
  try {
    await axios.delete(`repair-orders/${props.id}/`, {
      headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}
    })
    router.push({name: 'OrderList'})
  } catch (e) {
    console.error('Ошибка deleteOrder:', e)
  }
}

const selectedPavilion = computed(() => pavilions.value.find(p => p.id === order.value.pavilion) || null)
const repairStates = ['граффити', 'плановый ремонт', 'срочный ремонт']
const lastDamagedImage = computed(() => {
  if (!selectedPavilion.value) return null
  const imgs = selectedPavilion.value.images || []
  return [...imgs].reverse().find(img => repairStates.includes(img.confirmed_state)) || null
})
const pavilionPhoto = computed(() => lastDamagedImage.value?.image_url || '')
const pavilionProblem = computed(() => lastDamagedImage.value?.confirmed_state || '')
const filteredPavilions = computed(() => pavilions.value.filter(p => p.requires_repair && !ordersList.value.some(o => o.pavilion === p.id && o.status !== 'done')))
const filteredEmployees = computed(() => {
  if (!selectedPavilion.value) return []
  return employees.value.filter(e => e.district === selectedPavilion.value.district && (!selectedPavilion.value.region || e.region === selectedPavilion.value.region))
})
const workload = computed(() => ordersList.value.filter(o => o.employee?.id === order.value.employee_id && o.scheduled_for === order.value.scheduled_for).length)

watch(() => order.value.pavilion, async (newVal) => {
  if (newVal && isCreateMode.value) {
    try {
      const res = await axios.get(`pavilions/${newVal}/available_images/`, {
        headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}
      })
      availableImages.value = res.data
    } catch (e) {
      console.error('Ошибка загрузки изображений:', e)
    }
  }
})

onMounted(async () => {
  await fetchCurrentUser()
  await fetchMeta()
  await fetchOrder()
})

watch(() => props.id, async () => {
  loading.value = true
  await fetchCurrentUser()
  await fetchMeta()
  await fetchOrder()
})
</script>

<style scoped>
.order-edit-container {
  max-width: 700px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  color: #333;
}
.page-title {
  font-size: 1.75rem;
  margin-bottom: 1rem;
  text-align: center;
}
.loading {
  text-align: center;
  padding: 2rem 0;
  color: #666;
}
.order-form {
  background: #fff;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.form-group label {
  font-weight: 600;
}
.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.95rem;
  font-family: inherit;
}
.readonly-block {
  background: #f9fafb;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
}

.image-thumb {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.image-info {
  font-size: 0.9rem;
  color: #374151;
  font-weight: 500;
  text-align: center;
  margin-top: 0.5rem;
}

.image-carousel {
  display: flex;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  gap: 1rem;
  scroll-snap-type: x mandatory;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.image-card {
  flex: 0 0 auto;
  width: 280px;
  scroll-snap-align: start;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}


.carousel {
  width: 100%;
  height: 200px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 0.5rem;
}

.carousel-img {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

.carousel-caption {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #374151;
  font-weight: 500;
  text-align: center;
}

.carousel-checkbox {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #111827;
}
.pavilion-info {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.helper-text {
  font-size: 0.85rem;
  color: #6b7280;
}
.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: flex-start;
}
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  text-align: center;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.95rem;
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
