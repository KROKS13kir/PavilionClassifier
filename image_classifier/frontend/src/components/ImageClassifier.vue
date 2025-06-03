<template>
  <div class="classifier-block">
    <!-- Заголовок -->
    <h4 class="classifier-title">Загрузка и классификация изображений</h4>

    <!-- Зона загрузки -->
    <div class="file-upload">
      <label class="upload-label">
        <input type="file" multiple @change="handleFiles"/>
        Выбрать изображения
      </label>
      <button
          @click="predict"
          :disabled="!selectedFiles.length || loading"
          class="predict-btn"
      >
        {{ loading ? 'Загрузка...' : 'Получить прогноз' }}
      </button>
    </div>

    <!-- Список файлов -->
    <ul v-if="selectedFiles.length" class="file-list">
      <li v-for="(file, i) in selectedFiles" :key="i" class="file-item">
        {{ file.name }}
        <button @click="removeFile(i)" class="delete-btn">✕</button>
      </li>
    </ul>

    <!-- Превью изображений -->
    <div v-for="(img, i) in previewImages" :key="i" class="image-preview">
      <img :src="img.preview" class="preview-img"/>
      <p class="preview-meta">
        <strong>Класс:</strong> {{ img.predicted_class }} ({{ (img.confidence * 100).toFixed(1) }}%)
      </p>
      <select v-model="img.confirmed_state" class="select-state">
        <option disabled value="">— Выберите состояние —</option>
        <option value="не требует ремонта">не требует ремонта</option>
        <option value="граффити">граффити</option>
        <option value="плановый ремонт">плановый ремонт</option>
        <option value="срочный ремонт">срочный ремонт</option>
      </select>
      <button @click="removeFile(i)" class="delete-btn mt-2">Удалить</button>
    </div>

    <!-- Загрузка выбранных -->
    <button
        v-if="previewImages.length"
        @click="emitSave"
        class="upload-btn"
    >
      Сохранить выбор
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  apiPredictUrl: { type: String, required: true }
})
const emit = defineEmits(['save'])

const selectedFiles = ref([])
const previewImages = ref([])
const loading = ref(false)

function handleFiles(e) {
  Array.from(e.target.files)
    .filter(f => !selectedFiles.value.some(x => x.name === f.name))
    .forEach(f => selectedFiles.value.push(f))
  e.target.value = ''
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
  previewImages.value.splice(index, 1)
}

async function predict() {
  loading.value = true
  const fd = new FormData()
  selectedFiles.value.forEach(f => fd.append('images', f))

  try {
    const { data } = await axios.post(props.apiPredictUrl, fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('access')}`
      }
    })
    previewImages.value = data.map(pred => {
      const file = selectedFiles.value.find(f => f.name === pred.file_name)
      return {
        file,
        preview: URL.createObjectURL(file),
        predicted_class: pred.predicted_class,
        confidence: pred.confidence,
        confirmed_state: pred.predicted_class
      }
    })
  } catch (err) {
    console.error(err)
    alert('Не удалось получить прогноз')
  } finally {
    loading.value = false
  }
}

function emitSave() {
  const result = previewImages.value.map(img => ({
    ...img,
    confirmed_state: img.confirmed_state || img.predicted_class
  }))
  emit('save', result)
  selectedFiles.value = []
  previewImages.value = []
}
</script>

<style scoped>
.classifier-block {
  margin-top: 2rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
  font-size: 0.9rem;
}
.classifier-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Файлы и кнопки */
.file-upload {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: center;
}

.upload-label {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  cursor: pointer;
}
.upload-label input[type="file"] {
  display: none;
}

.predict-btn {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}
.predict-btn:hover {
  background: #2563eb;
}

/* Файлы */
.file-list {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}
.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f3f4f6;
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
}

/* Превью */
.image-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}
.preview-img {
  width: 100%;
  max-height: 10rem;
  object-fit: contain;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}
.preview-meta {
  margin-bottom: 0.25rem;
}
.select-state {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

/* Кнопки */
.delete-btn {
  background: none;
  color: #ef4444;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}
.delete-btn:hover {
  color: #dc2626;
}
.upload-btn {
  background: #f59e0b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  margin-top: 1rem;
  cursor: pointer;
}
.upload-btn:hover {
  background: #d97706;
}
</style>
