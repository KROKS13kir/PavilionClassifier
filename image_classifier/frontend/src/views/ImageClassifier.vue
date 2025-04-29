<template>
  <div class="container">
    <h2>Классификация изображений</h2>

    <!-- Шаг 1. Загрузка изображений -->
    <label class="custom-file-upload">
      <input type="file" multiple @change="handleFiles"/>
      Выбрать изображения
    </label>
    <ul v-if="selectedFiles.length">
      <li v-for="(file, index) in selectedFiles" :key="index">
        {{ file.name }}
        <button @click="removeFile(index)">Удалить</button>
      </li>
    </ul>
    <button @click="handlePredict" :disabled="!selectedFiles.length">Получить прогноз</button>


    <!-- Шаг 2. Отображение и подтверждение -->
    <div v-for="(img, index) in previewImages" :key="index" class="image-block">
      <img :src="img.preview" class="preview" v-if="img.preview" />
      <p>Файл: {{ img.file.name }}</p>
      <p><strong>Класс:</strong> {{ img.predicted_class }}</p>
      <p><strong>Уверенность:</strong> {{ (img.confidence * 100).toFixed(2) }}%</p>

      <select v-model="img.confirmed_state">
        <option disabled value="">Состояние (подтвердить/изменить)</option>
        <option value="не требует ремонта">не требует ремонта</option>
        <option value="граффити">граффити</option>
        <option value="плановый ремонт">плановый ремонт</option>
        <option value="срочный ремонт">срочный ремонт</option>
      </select>

      <!-- ✅ Перемещено сюда -->
      <button @click="removeFile(index)">Удалить</button>
    </div>


    <!-- Шаг 3. Форма карточки -->
    <form v-if="previewImages.length" @submit.prevent="handleSubmit" class="form">
      <h3>Данные карточки павильона</h3>
      <input v-model="form.mpv_code" placeholder="Код МПВ" />
      <input v-model="form.stop_name" placeholder="Название остановки" />
      <input v-model="form.street" placeholder="Улица" />

      <select v-model="form.district">
        <option disabled value="">Округ</option>
        <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>

      <div class="autocomplete">
        <input
            type="text"
            v-model="regionSearch"
            placeholder="Район"
            @input="filterRegions"
            @focus="showRegionDropdown = true"
        />
        <ul v-if="showRegionDropdown && filteredRegions.length" class="dropdown">
          <li
              v-for="region in filteredRegions"
              :key="region.id"
              @click="selectRegion(region)"
          >
            {{ region.name }}
          </li>
        </ul>
      </div>

      <input v-model="form.pavilion_number" placeholder="Номер павильона" />

      <select v-model="form.category">
        <option disabled value="">Категория</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
      </select>

      <input v-model="form.pavilion_class" placeholder="Класс павильона" />

      <select v-model="form.balance_holder">
        <option disabled value="">Балансодержатель</option>
        <option value="Город">Город</option>
        <option value="Частная">Частная</option>
      </select>

      <input v-model="form.address" placeholder="Адрес" />

      <button type="submit">Сохранить карточку + изображения</button>
    </form>

    <!-- Итог -->
    <div v-if="results.length" class="results">
      <h3>Успешно сохранено:</h3>
      <div v-for="(res, i) in results" :key="i" class="card">
        <img :src="backendUrl + res.image" class="preview" />
        <p><strong>Класс:</strong> {{ res.predicted_class }}</p>
        <p><strong>Уверенность:</strong> {{ (res.confidence * 100).toFixed(2) }}%</p>
        <p><strong>Подтверждённое состояние:</strong> {{ res.confirmed_state }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const backendUrl = 'http://localhost:8000'

const districts = ref([])
const regions = ref([])
const selectedFiles = ref([])

const form = ref({
  mpv_code: '',
  stop_name: '',
  street: '',
  district: '',
  region: '',
  pavilion_number: '',
  category: '',
  pavilion_class: '',
  balance_holder: '',
  address: '',
})

const previewImages = ref([]) // { file, predicted_class, confidence, confirmed_state }
const results = ref([])

const regionSearch = ref('')
const showRegionDropdown = ref(false)
const filteredRegions = ref([])


const filterRegions = () => {
  const query = regionSearch.value.toLowerCase()
  filteredRegions.value = regions.value.filter(r =>
    r.name.toLowerCase().includes(query)
  )
}

const selectRegion = (region) => {
  form.value.region = region.id
  regionSearch.value = region.name
  showRegionDropdown.value = false
}

onMounted(async () => {
  const d = await axios.get(`${backendUrl}/api/districts/`)
  const r = await axios.get(`${backendUrl}/api/regions/`)
  districts.value = d.data
  regions.value = r.data
  filteredRegions.value = r.data
})

const handleFiles = (event) => {
  const newFiles = Array.from(event.target.files)

  // Проверка на дубликаты по имени файла
  newFiles.forEach(file => {
    if (!selectedFiles.value.some(f => f.name === file.name)) {
      selectedFiles.value.push(file)
    }
  })

  // Сброс input, чтобы можно было выбрать тот же файл снова при желании
  event.target.value = ''
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  previewImages.value.splice(index, 1)
}


const handlePredict = async () => {
  const fd = new FormData()
  selectedFiles.value.forEach(file => {
    fd.append('images', file)
  })

  try {
      const res = await axios.post(`${backendUrl}/api/predict/`, fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('access')}`
      }
    })

    previewImages.value = res.data.map(pred => {
      const file = selectedFiles.value.find(f => f.name === pred.file_name)
      return {
        file,
        predicted_class: pred.predicted_class,
        confidence: pred.confidence,
        confirmed_state: pred.predicted_class,
        preview: URL.createObjectURL(file)  // 💡 вот оно
      }
    })

  } catch (err) {
    alert('Ошибка при получении прогноза')
    console.error(err)
  }
}

const handleSubmit = async () => {
  const fd = new FormData()
  for (const key in form.value) {
    fd.append(key, form.value[key])
  }

  previewImages.value.forEach((img, index) => {
    fd.append(`images[${index}].image`, img.file)
    fd.append(`images[${index}].confirmed_state`, img.confirmed_state)
  })

  try {
    const response = await axios.post(`${backendUrl}/api/pavilion/`, fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('access')}`
      }
    })
    alert('Успешно сохранено!')
    results.value = response.data.images || []
    previewImages.value = []
    selectedFiles.value = []
  } catch (error) {
    console.error(error)
    alert('Ошибка при сохранении карточки')
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}
input, select {
  display: block;
  margin-bottom: 10px;
  padding: 8px;
  width: 100%;
}
button {
  margin-top: 10px;
  padding: 10px;
}
.image-block {
  border: 1px dashed #aaa;
  padding: 10px;
  margin-bottom: 10px;
}
.results {
  margin-top: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}
.card {
  border: 1px solid #ccc;
  padding: 10px;
}
.preview {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}
.custom-file-upload {
  display: inline-block;
  padding: 10px 15px;
  background: #4285f4;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.custom-file-upload input[type="file"] {
  display: none;
}
.autocomplete {
  position: relative;
}

.dropdown {
  position: absolute;
  background: white;
  border: 1px solid #ccc;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  padding: 0;
  margin: 0;
  list-style: none;
}

.dropdown li {
  padding: 8px;
  cursor: pointer;
}

.dropdown li:hover {
  background-color: #f0f0f0;
}

</style>
