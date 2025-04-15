<template>
  <div class="container">
    <h2>Классификация изображений</h2>
    <form @submit.prevent="handleSubmit" class="form">
      <input type="file" multiple @change="handleFiles" />
      <button type="submit">Отправить</button>
    </form>

    <div v-if="results.length" class="results">
      <h3>Результаты:</h3>
      <div v-for="(result, index) in results" :key="index" class="card">
        <img :src="backendUrl + result.image" alt="preview" class="preview" />
        <p><strong>Класс:</strong> {{ result.predicted_class }}</p>
        <p><strong>Уверенность:</strong> {{ (result.confidence * 100).toFixed(2) }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const backendUrl = 'http://localhost:8000'
const selectedFiles = ref([])
const results = ref([])

const handleFiles = (event) => {
  selectedFiles.value = Array.from(event.target.files)
}

const handleSubmit = async () => {
  const formData = new FormData()
  selectedFiles.value.forEach(file => formData.append('images', file))

  try {
    const response = await axios.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('access')}`,
      }
    })
    results.value = response.data
  } catch (error) {
    alert('Ошибка при загрузке изображений')
    console.error(error)
  }
}
</script>

<style scoped>
.container {
  max-width: 700px;
  margin: auto;
  padding: 20px;
}
.form {
  margin-bottom: 20px;
}
button {
  margin-top: 10px;
  padding: 10px;
}
.results {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}
.card {
  border: 1px solid #ccc;
  padding: 10px;
}
.preview {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}
</style>
