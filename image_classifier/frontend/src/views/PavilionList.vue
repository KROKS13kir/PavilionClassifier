<template>
  <div class="pavilion-list container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Все павильоны</h1>

    <div v-if="loading" class="text-center">Загрузка...</div>
    <div v-else-if="!pavilions.length" class="text-center text-gray-500">Нет данных</div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
          v-for="p in pavilions"
          :key="p.id"
          @click="goToPavilion(p.id)"
      >
        <h2 class="font-semibold text-lg">{{ p.stop_name }} ({{ p.mpv_code }})</h2>
        <p class="text-sm text-gray-600">
          {{ p.street }}, {{ getDistrictName(p.district) }}, {{ getRegionName(p.region) }}
        </p>
        <button
          @click.stop="deletePavilion(p.id)"
          class="mt-3 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Удалить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const backendUrl = 'http://localhost:8000'
const pavilions = ref([])
const districts = ref([])
const regions = ref([])
const loading = ref(true)

const router = useRouter()

const fetchPavilions = async () => {
  loading.value = true
  try {
    const { data } = await axios.get(`${backendUrl}/api/pavilions/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
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

const goToPavilion = (id) => {
  if (!id) {
    console.error('ID пустой, переход невозможен')
    return
  }
  router.push(`/pavilions/${id}`) // 💡 проще и надёжнее
}


const deletePavilion = async (id) => {
  if (!confirm('Удалить павильон?')) return
  try {
    await axios.delete(`${backendUrl}/api/pavilions/${id}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    fetchPavilions()
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await fetchMetaData()
  await fetchPavilions()
})
</script>

<style scoped>
.pavilion-list .cursor-pointer:hover {
  transition: background-color 0.2s;
}
</style>
