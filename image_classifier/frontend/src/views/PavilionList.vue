<template>
  <div class="pavilion-list">
    <header class="pl-header">
      <h1 class="pl-title">Список павильонов</h1>
      <button class="pl-add-button" @click="router.push('/pavilions/create')">+ Новый павильон</button>
    </header>

    <section class="pl-filters">
      <div class="pl-filter-wrapper">
        <input
          v-model="search"
          type="text"
          placeholder="Поиск по всем полям..."
          class="pl-filter-input"
        />
        <button
          v-if="search"
          @click="search = ''"
          class="pl-clear-btn"
          aria-label="Очистить поиск"
        >&times;</button>
      </div>
      <select v-model="selectedDistrict" class="pl-filter-select">
        <option value="">Все округа</option>
        <option v-for="d in uniqueDistricts" :key="d" :value="d">{{ d }}</option>
      </select>
      <select v-model="selectedRegion" class="pl-filter-select">
        <option value="">Все районы</option>
        <option v-for="r in uniqueRegions" :key="r" :value="r">{{ r }}</option>
      </select>
      <select v-model="selectedCondition" class="pl-filter-select">
        <option value="">Состояние износа</option>
        <option v-for="cond in uniqueConditions" :key="cond" :value="cond">{{ cond }}</option>
      </select>
    </section>

    <div v-if="loading" class="pl-placeholder">Загрузка...</div>
    <div v-else-if="!filteredPavilions.length" class="pl-placeholder">Нет данных</div>

    <div v-else class="pl-table-container">
      <table class="pl-table">
        <thead>
          <tr>
            <th>Код МПВ</th>
            <th>Остановка</th>
            <th>Округ</th>
            <th>Район</th>
            <th>№</th>
            <th>Категория</th>
            <th>Класс</th>
            <th>Баланс</th>
            <th>Адрес</th>
            <th>Статус</th>
            <th>Наряд</th>
            <th>Удалить</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filteredPavilions" :key="p.id">
            <td @click="goToPavilion(p.id)">{{ p.mpv_code }}</td>
            <td @click="goToPavilion(p.id)">{{ p.stop_name }}</td>
            <td @click="goToPavilion(p.id)">{{ getDistrictName(p.district) }}</td>
            <td @click="goToPavilion(p.id)">{{ getRegionName(p.region) }}</td>
            <td @click="goToPavilion(p.id)">{{ p.pavilion_number }}</td>
            <td @click="goToPavilion(p.id)">{{ p.category }}</td>
            <td @click="goToPavilion(p.id)">{{ p.pavilion_class }}</td>
            <td @click="goToPavilion(p.id)">{{ p.balance_holder }}</td>
            <td @click="goToPavilion(p.id)">{{ p.address }}</td>
            <td @click="goToPavilion(p.id)">{{ p.status }}</td>
            <td class="pl-cell-center">
              <span v-if="p.requires_repair" class="pl-repair-yes">✔</span>
              <span v-else class="pl-repair-no">–</span>
            </td>
            <td class="pl-cell-center">
              <button class="pl-delete-button" @click="deletePavilion(p.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const backendUrl = '/api'
const pavilions = ref([])
const districts = ref([])
const regions = ref([])
const loading = ref(true)
const search = ref('')
const selectedDistrict = ref('')
const selectedRegion = ref('')
const selectedCondition = ref('')

const router = useRouter()


const fetchPavilions = async () => {
  loading.value = true
  try {
    const {data} = await axios.get(`${backendUrl}/api/pavilions/`, {
      headers: {Authorization: `Bearer ${localStorage.getItem('access')}`}
    })
    pavilions.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchMetaData = async () => {
  try {
    const [dRes, rRes] = await Promise.all([
      axios.get(`${backendUrl}/api/districts/`),
      axios.get(`${backendUrl}/api/regions/`)
    ])
    districts.value = dRes.data
    regions.value = rRes.data
  } catch (e) {
    console.error(e)
  }
}

const getDistrictName = (id) => {
  return (districts.value.find(d => d.id === id) || {}).name || ''
}

const getRegionName = (id) => {
  return (regions.value.find(r => r.id === id) || {}).name || ''
}

const getLastImageCondition = (pavilion) => {
  if (!pavilion.images || !pavilion.images.length) return null
  const lastImage = [...pavilion.images].sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at))[0]
  return (lastImage.confirmed_state || lastImage.predicted_class || '').toLowerCase()
}

const uniqueDistricts = computed(() => [...new Set(pavilions.value.map(p => getDistrictName(p.district)).filter(Boolean))])
const uniqueRegions = computed(() => [...new Set(pavilions.value.map(p => getRegionName(p.region)).filter(Boolean))])
const uniqueConditions = computed(() => [...new Set(pavilions.value.map(getLastImageCondition).filter(Boolean))])

const filteredPavilions = computed(() => {
  return pavilions.value.filter(p => {
    const imageCondition = getLastImageCondition(p)
    return (
      (!search.value || JSON.stringify(p).toLowerCase().includes(search.value.toLowerCase())) &&
      (!selectedDistrict.value || getDistrictName(p.district) === selectedDistrict.value) &&
      (!selectedRegion.value || getRegionName(p.region) === selectedRegion.value) &&
      (!selectedCondition.value || imageCondition === selectedCondition.value)
    )
  })
})

const goToPavilion = (id) => {
  if (!id) {
    console.error('ID пустой, переход невозможен')
    return
  }
  router.push(`/pavilions/${id}`)
}

const deletePavilion = async (id) => {
  if (!confirm('Удалить павильон?')) return;
  try {
    await axios.delete(`${backendUrl}/api/pavilions/${id}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    });
    await fetchPavilions();
  } catch (e) {
    console.error('Ошибка при удалении павильона', e);
  }
}

onMounted(async () => {
  await fetchMetaData()
  await fetchPavilions()
})
</script>

<style scoped>
.pl-filter-wrapper {
  position: relative;
}
.pl-clear-btn {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.pl-clear-btn:hover {
  color: #6b7280;
}

.pavilion-list {
  max-width: 90%;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Inter', sans-serif;
  color: #333;
}
.pl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.pl-title {
  font-size: 32px;
  font-weight: 700;
}
.pl-add-button {
  background-color: #1e40af;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.pl-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  column-gap: 24px;
  row-gap: 16px;
  margin-bottom: 24px;
}
.pl-filter-input,
.pl-filter-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  min-width: 0;
}
.pl-placeholder {
  text-align: center;
  padding: 40px 0;
  font-size: 18px;
  color: #6b7280;
}
.pl-table-container {
  max-height: 60vh;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}
.pl-table {
  width: 100%;
  border-collapse: collapse;
}
.pl-table th,
.pl-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  white-space: nowrap;
}
.pl-table thead th {
  position: sticky;
  top: 0;
  background: #f8fafc;
  z-index: 10;
}
.pl-cell-center {
  text-align: center;
}
.pl-repair-yes {
  color: #dc2626;
  font-weight: 600;
}
.pl-repair-no {
  color: #9ca3af;
}
.pl-delete-button {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 14px;
}
.pl-delete-button:hover {
  text-decoration: underline;
}
</style>
