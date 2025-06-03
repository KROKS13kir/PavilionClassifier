<template>
  <div class="card-form-container">
    <div class="card-content">
      <h3 class="section-title">Данные карточки павильона</h3>
      <form @submit.prevent="handleSubmit" class="form-grid">
        <!-- fields same as before -->
        <div class="form-group"><label>Код МПВ</label><input v-model="form.mpv_code" placeholder="Код МПВ" /></div>
        <div class="form-group"><label>Остановка</label><input v-model="form.stop_name" placeholder="Название остановки" /></div>
        <div class="form-group"><label>Улица</label><input v-model="form.street" placeholder="Улица" /></div>
        <div class="form-group"><label>Округ</label>
          <select v-model="form.district">
            <option disabled value="">Выберите округ</option>
            <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div class="form-group autocomplete"><label>Район</label>
          <input type="text" v-model="regionSearch" placeholder="Район" @input="filterRegions" @focus="showRegionDropdown = true" />
          <ul v-if="showRegionDropdown && filteredRegions.length" class="dropdown">
            <li v-for="region in filteredRegions" :key="region.id" @click="selectRegion(region)">{{ region.name }}</li>
          </ul>
        </div>
        <div class="form-group"><label>№ павильона</label><input v-model="form.pavilion_number" placeholder="Номер павильона" /></div>
        <div class="form-group"><label>Категория</label>
          <select v-model="form.category">
            <option disabled value="">Выберите категорию</option>
            <option v-for="[value,label] in categoryChoices" :key="value" :value="value">{{ label }}</option>
          </select>
        </div>
        <div class="form-group"><label>Класс</label><input v-model="form.pavilion_class" placeholder="Класс павильона" /></div>
        <div class="form-group"><label>Балансодержатель</label>
          <select v-model="form.balance_holder">
            <option disabled value="">Выберите балансодержателя</option>
            <option v-for="[value,label] in balanceHolderChoices" :key="value" :value="value">{{ label }}</option>
          </select>
        </div>
        <div class="form-group"><label>Адрес</label><input v-model="form.address" placeholder="Адрес" /></div>
        <div class="form-group"><label>Статус</label>
          <select v-model="form.status">
            <option disabled value="">Выберите статус</option>
            <option v-for="[value,label] in statusChoices" :key="value" :value="value">{{ label }}</option>
          </select>
        </div>
      </form>
    </div>

    <div class="classification-content">
      <h3 class="section-title">Классификация изображений</h3>
      <div class="button-row">
        <label class="custom-file-upload">
          <input type="file" multiple @change="handleFiles"/>
          Выбрать изображения
        </label>
        <button class="action-btn" :disabled="!selectedFiles.length" @click="handlePredict">Получить прогноз</button>
      </div>
      <div v-if="previewImages.length" class="image-carousel">
        <button class="carousel-btn prev" @click="prevImage">‹</button>
        <div class="carousel-track" :style="{ transform: `translateX(-${currentIndex*100}%)` }">
          <div v-for="(img,index) in previewImages" :key="index" class="carousel-item">
            <img :src="img.preview" class="preview-image"/>
            <div class="image-info">
              <p class="info-line"><strong>Файл:</strong> {{ img.file.name }}</p>
              <p class="info-line"><strong>Класс:</strong> {{ img.predicted_class }}</p>
              <p class="info-line"><strong>Уверенность:</strong> {{ (img.confidence * 100).toFixed(2) }}%</p>
              <label class="confirm-label">Подтвердить состояние:</label>
              <select v-model="img.confirmed_state" class="confirm-select">
                <option disabled value="">Выберите...</option>
                <option value="не требует ремонта">не требует ремонта</option>
                <option value="граффити">граффити</option>
                <option value="плановый ремонт">плановый ремонт</option>
                <option value="срочный ремонт">срочный ремонт</option>
              </select>
              <button @click.prevent="removeFile(index)" class="delete-img-btn">Удалить</button>
            </div>
          </div>
        </div>
        <button class="carousel-btn next" @click="nextImage">›</button>
      </div>
      <div class="button-row">
        <button class="save-btn" :disabled="!previewImages.length" @click="handleSubmit">Сохранить карточку и
          изображения
        </button>
      </div>
      <div v-if="saved" class="notification">Данные успешно сохранены!</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const backendUrl = '/api'
const districts = ref([])
const regions = ref([])
const selectedFiles = ref([])
const form = ref({ mpv_code:'', stop_name:'', street:'', district:'', region:'', pavilion_number:'', category:'', pavilion_class:'', balance_holder:'', address:'', status:'' })
const previewImages = ref([])
const saved = ref(false)
const regionSearch = ref('')
const showRegionDropdown = ref(false)
const filteredRegions = ref([])
const categoryChoices = ref([])
const balanceHolderChoices = ref([])
const statusChoices = ref([])
const currentIndex = ref(0)

onMounted(async () => {
  const [d, r, c] = await Promise.all([
    axios.get(`${backendUrl}/api/districts/`),
    axios.get(`${backendUrl}/api/regions/`),
    axios.get(`${backendUrl}/api/pavilion_choices/`)
  ])
  districts.value = d.data
  regions.value = r.data
  filteredRegions.value = r.data
  categoryChoices.value = c.data.category
  balanceHolderChoices.value = c.data.balance_holder
  statusChoices.value = c.data.status
})

const prevImage = () => {
  currentIndex.value = (currentIndex.value - 1 + previewImages.value.length) % previewImages.value.length
}
const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % previewImages.value.length
}

const filterRegions = () => {
  const q = regionSearch.value.toLowerCase()
  filteredRegions.value = regions.value.filter(r => r.name.toLowerCase().includes(q))
}
const selectRegion = region => { form.value.region = region.id; regionSearch.value = region.name; showRegionDropdown.value = false }

const handleFiles = e => {
  const files = Array.from(e.target.files)
  files.forEach(f => { if (!selectedFiles.value.some(s => s.name === f.name)) selectedFiles.value.push(f) })
  e.target.value = ''
}
const removeFile = i => { selectedFiles.value.splice(i, 1); previewImages.value.splice(i, 1) }

const handlePredict = async () => {
  const fd = new FormData()
  selectedFiles.value.forEach(f => fd.append('images', f))
  const { data } = await axios.post(`${backendUrl}/api/predict/`, fd, {
    headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('access')}` }
  })
  previewImages.value = data.map(pred => {
    const file = selectedFiles.value.find(f => f.name === pred.file_name)
    return { file, predicted_class: pred.predicted_class, confidence: pred.confidence, confirmed_state: pred.predicted_class, preview: URL.createObjectURL(file) }
  })
}

const handleSubmit = async () => {
  const fd = new FormData()
  Object.entries(form.value).forEach(([k, v]) => fd.append(k, v))
  previewImages.value.forEach((img, i) => { fd.append(`images[${i}].image`, img.file); fd.append(`images[${i}].confirmed_state`, img.confirmed_state) })
  try {
    await axios.post(`${backendUrl}/api/pavilion/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    // Показываем уведомление об успехе
    saved.value = true
    // Сбрасываем форму через несколько секунд
    setTimeout(() => { saved.value = false }, 3000)
    selectedFiles.value = []
    previewImages.value = []
  } catch (error) {
    console.error(error)
    alert('Ошибка при сохранении карточки')
  }
}
</script>

<style scoped>
.card-form-container {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  max-width: 1200px;
  margin: 24px auto;
  padding: 16px;
  font-family: 'Inter', sans-serif;
}
.card-content,
.classification-content {
  flex: 1 1 45%;
}
.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  grid-auto-rows: minmax(50px, auto);
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 4px;
  font-size: 14px;
  color: #555;
}
.form-group input,
.form-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}
.autocomplete {
  position: relative;
}
.autocomplete .dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ccc;
  max-height: 150px;
  overflow-y: auto;
  z-index: 10;
}
.autocomplete .dropdown li {
  padding: 8px;
  cursor: pointer;
}
.autocomplete .dropdown li:hover {
  background: #f3f4f6;
}
.custom-file-upload {
  display: inline-block;
  margin-bottom: 16px;
  padding: 10px 20px;
  background-color: #2563eb;
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
}
.custom-file-upload input {
  display: none;
}
.button-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.action-btn,
.save-btn {
  background-color: #1e40af;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}
.action-btn:disabled,
.save-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
.save-btn {
  display: block;
  margin: 24px auto;
}
.image-carousel {
  position: relative;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 16px;
}
.carousel-track {
  display: flex;
  transition: transform 0.3s ease;
}
.carousel-item {
  min-width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
}
.preview-image {
  width: 100%;
  max-width: 400px;
  height: auto;
  margin: 0 auto;
  display: block;
}
.image-info {
  width: 100%;
  max-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.info-line {
  margin: 4px 0;
}
.confirm-label {
  font-size: 14px;
  color: #333;
  margin-top: 8px;
}
.confirm-select {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.delete-img-btn {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  margin-top: 8px;
}
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.8);
  border: none;
  font-size: 24px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}
.carousel-btn.prev {
  left: 8px;
}
.carousel-btn.next {
  right: 8px;
}
.notification {
  margin-top: 16px;
  padding: 12px;
  background-color: #d1fae5;
  border: 1px solid #10b981;
  border-radius: 4px;
  color: #065f46;
}
</style>
