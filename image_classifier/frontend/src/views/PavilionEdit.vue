<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Редактирование павильона</h1>

    <div v-if="loading" class="text-center">Загрузка...</div>
    <div v-else-if="!pavilion" class="text-red-600">Ошибка загрузки павильона</div>

    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block font-semibold mb-1">Код МПВ</label>
          <input v-model="pavilion.mpv_code" class="w-full p-2 border rounded" />
        </div>

        <div>
          <label class="block font-semibold mb-1">Название остановки</label>
          <input v-model="pavilion.stop_name" class="w-full p-2 border rounded" />
        </div>

        <div>
          <label class="block font-semibold mb-1">Улица</label>
          <input v-model="pavilion.street" class="w-full p-2 border rounded" />
        </div>

        <div>
          <label class="block font-semibold mb-1">Округ</label>
          <select v-model="pavilion.region" class="w-full p-2 border rounded">
            <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </div>

        <div>
          <label class="block font-semibold mb-1">Район</label>
          <select v-model="pavilion.district" class="w-full p-2 border rounded">
            <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
      </div>

      <div class="mt-6 flex justify-between">
        <button @click="savePavilion" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
          Сохранить
        </button>
        <router-link to="/pavilions" class="text-blue-600 hover:underline">← Назад к списку</router-link>
      </div>

      <hr class="my-6" />

      <h2 class="text-xl font-semibold mb-4">Фотографии</h2>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <div v-for="img in pavilion.images" :key="img.id" class="border rounded p-2 shadow">
          <img v-if="img.image_url" :src="img.image_url" class="w-full h-40 object-cover rounded mb-2" />
          <p><strong>Класс:</strong> {{ img.predicted_class }}</p>

          <label class="block mt-2">Подтв. состояние</label>
          <select v-model="img.confirmed_state" class="w-full p-1 border rounded">
            <option value="не требует ремонта">не требует ремонта</option>
            <option value="граффити">граффити</option>
            <option value="плановый ремонт">плановый ремонт</option>
            <option value="срочный ремонт">срочный ремонт</option>
          </select>

          <div class="mt-2 flex justify-between">
            <button @click="saveImage(img)" class="text-sm px-2 py-1 bg-yellow-400 text-white rounded">Сохранить</button>
            <button @click="deleteImage(img.id)" class="text-sm px-2 py-1 bg-red-500 text-white rounded">Удалить</button>
          </div>
        </div>
      </div>

      <div class="mt-6">
        <h3 class="text-lg font-semibold mb-2">Добавить изображения</h3>
        <input type="file" multiple @change="handleUpload" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const backendUrl = 'http://localhost:8000'
const route = useRoute()
const router = useRouter()
const id = ref(null)

const pavilion = ref(null)
const regions = ref([])
const districts = ref([])
const loading = ref(true)

const fetchPavilion = async () => {
  try {
    const { data } = await axios.get(`${backendUrl}/api/pavilions/${id.value}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    pavilion.value = data
  } catch (e) {
    console.error(e)
  }
}

const fetchMeta = async () => {
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

const savePavilion = async () => {
  try {
    await axios.patch(`${backendUrl}/api/pavilions/${id.value}/`, pavilion.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    alert('Сохранено')
  } catch (e) {
    console.error(e)
  }
}

const saveImage = async (img) => {
  try {
    await axios.patch(`${backendUrl}/api/images/${img.id}/`, {
      confirmed_state: img.confirmed_state
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
  } catch (e) {
    console.error(e)
  }
}

const deleteImage = async (imageId) => {
  if (!confirm('Удалить изображение?')) return
  try {
    await axios.delete(`${backendUrl}/api/images/${imageId}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    await fetchPavilion()
  } catch (e) {
    console.error(e)
  }
}

const handleUpload = async (e) => {
  const files = Array.from(e.target.files)
  const fd = new FormData()
  files.forEach(file => fd.append('images', file))

  try {
    const res = await axios.post(`${backendUrl}/api/predict/`, fd, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access')}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    for (let i = 0; i < files.length; i++) {
      const form = new FormData()
      form.append('images[0].image', files[i])
      form.append('images[0].confirmed_state', res.data[i].predicted_class)
      form.append('pavilion', id.value)

      await axios.post(`${backendUrl}/api/pavilion/`, form, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access')}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    await fetchPavilion()
  } catch (e) {
    console.error(e)
    alert('Ошибка при добавлении изображений')
  }
}

watch(
  () => route.params.id,
  async (newId) => {
    if (!newId) return
    id.value = newId
    loading.value = true
    await fetchMeta()
    await fetchPavilion()
    loading.value = false
  },
  { immediate: true }
)
</script>