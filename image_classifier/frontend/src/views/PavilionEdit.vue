<template>
  <div class="pavilion-edit">
    <h1 class="page-title">Редактирование павильона</h1>

    <div v-if="loading" class="loading">Загрузка…</div>
    <div v-else-if="!pavilion" class="loading-error">Ошибка загрузки павильона</div>

    <div v-else class="edit-layout">
      <!-- Левая колонка: форма -->
      <div class="edit-form">
        <section class="form-section">
          <h2>Основные данные</h2>

          <div class="field" v-for="field in formFields" :key="field.key">
            <label>{{ field.label }}</label>
            <template v-if="field.type === 'select'">
              <select v-model="pavilion[field.key]">
                <option v-if="field.placeholder" disabled value="">{{ field.placeholder }}</option>
                <option v-for="option in field.options" :key="option.value || option.id"
                        :value="option.value || option.id">
                  {{ option.label || option.name }}
                </option>
              </select>
            </template>
            <template v-else>
              <input v-model="pavilion[field.key]" type="text"/>
            </template>
          </div>
        </section>

        <div class="form-actions">
          <button @click="savePavilion">Сохранить</button>
          <router-link to="/pavilions">← Назад</router-link>
        </div>
      </div>

      <!-- Правая колонка: карусель, ImageClassifier и изображение -->
      <div class="edit-carousel">
        <h2>Фотографии</h2>

        <div v-if="pavilion.images.length" class="carousel">
          <button class="carousel-btn prev" @click="prev">‹</button>
          <img
            :src="pavilion.images[currentIndex].image_url"
            class="carousel-image"
            alt="Фото павильона"
          />
          <button class="carousel-btn next" @click="next">›</button>
        </div>

        <div v-else class="no-images">Нет фото</div>

        <div class="image-meta" v-if="pavilion.images.length">
          <p><strong>Дата фото:</strong> {{ new Date(pavilion.images[currentIndex].uploaded_at).toLocaleString('ru-RU') }}</p>
          <p><strong>Класс:</strong> {{ pavilion.images[currentIndex].predicted_class }}</p>

          <div class="field">
            <label>Подтвердить состояние</label>
            <select v-model="pavilion.images[currentIndex].confirmed_state">
              <option value="не требует ремонта">не требует ремонта</option>
              <option value="граффити">граффити</option>
              <option value="плановый ремонт">плановый ремонт</option>
              <option value="срочный ремонт">срочный ремонт</option>
            </select>
          </div>

          <div class="image-actions">
            <button @click="saveImage(pavilion.images[currentIndex])">Сохранить</button>
            <button @click="deleteImage(pavilion.images[currentIndex].id)">Удалить</button>
          </div>
        </div>


        <!-- Блок ImageClassifier -->
        <div class="classifier-block">
          <ImageClassifier
            class="inline-classifier"
            apiPredictUrl="/api/predict/"
            @save="onNewImages"
          />
          <button
            v-if="newImages.length"
            @click="uploadConfirmed"
            class="classifier-upload-btn"
          >
            Загрузить новые изображения
          </button>
        </div>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ImageClassifier from '@/components/ImageClassifier.vue'


const route = useRoute()
const id = ref(null)
const pavilion = ref({ images: [] })
const regions = ref([])
const districts = ref([])
const loading = ref(true)
const categoryChoices = ref([])
const balanceHolderChoices = ref([])
const statusChoices = ref([])
const currentIndex = ref(0)
const newImages = ref([])

function prev() {
  currentIndex.value = (currentIndex.value - 1 + pavilion.value.images.length) % pavilion.value.images.length
}

function next() {
  currentIndex.value = (currentIndex.value + 1) % pavilion.value.images.length
}

const formFields = ref([
  { key: 'mpv_code', label: 'Код МПВ', type: 'text' },
  { key: 'stop_name', label: 'Название остановки', type: 'text' },
  { key: 'street', label: 'Улица', type: 'text' },
  {
    key: 'region',
    label: 'Округ',
    type: 'select',
    options: regions.value
  },
  {
    key: 'district',
    label: 'Район',
    type: 'select',
    options: districts.value
  },
  { key: 'pavilion_number', label: 'Номер павильона', type: 'text' },
  {
    key: 'category',
    label: 'Категория',
    type: 'select',
    options: categoryChoices.value.map(([value, label]) => ({ value, label })),
    placeholder: 'Выберите категорию'
  },
  { key: 'pavilion_class', label: 'Класс павильона', type: 'text' },
  {
    key: 'balance_holder',
    label: 'Балансодержатель',
    type: 'select',
    options: balanceHolderChoices.value.map(([value, label]) => ({ value, label })),
    placeholder: 'Выберите балансодержателя'
  },
  { key: 'address', label: 'Адрес', type: 'text' },
  {
    key: 'status',
    label: 'Статус',
    type: 'select',
    options: statusChoices.value.map(([value, label]) => ({ value, label })),
    placeholder: 'Выберите статус'
  }
])


async function fetchMeta() {
  const [dRes, rRes, cRes] = await Promise.all([
    axios.get(`districts/`),
    axios.get(`regions/`),
    axios.get(`pavilion_choices/`)
  ])
  districts.value = dRes.data
  regions.value = rRes.data
  categoryChoices.value = cRes.data.category
  balanceHolderChoices.value = cRes.data.balance_holder
  statusChoices.value = cRes.data.status

  formFields.value = [
    { key: 'mpv_code', label: 'Код МПВ', type: 'text' },
    { key: 'stop_name', label: 'Название остановки', type: 'text' },
    { key: 'street', label: 'Улица', type: 'text' },
    {
      key: 'region',
      label: 'Округ',
      type: 'select',
      options: regions.value
    },
    {
      key: 'district',
      label: 'Район',
      type: 'select',
      options: districts.value
    },
    { key: 'pavilion_number', label: 'Номер павильона', type: 'text' },
    {
      key: 'category',
      label: 'Категория',
      type: 'select',
      options: categoryChoices.value.map(([value, label]) => ({ value, label })),
      placeholder: 'Выберите категорию'
    },
    { key: 'pavilion_class', label: 'Класс павильона', type: 'text' },
    {
      key: 'balance_holder',
      label: 'Балансодержатель',
      type: 'select',
      options: balanceHolderChoices.value.map(([value, label]) => ({ value, label })),
      placeholder: 'Выберите балансодержателя'
    },
    { key: 'address', label: 'Адрес', type: 'text' },
    {
      key: 'status',
      label: 'Статус',
      type: 'select',
      options: statusChoices.value.map(([value, label]) => ({ value, label })),
      placeholder: 'Выберите статус'
    }
  ]
}


async function fetchPavilion() {
  const { data } = await axios.get(
    `pavilions/${id.value}/`,
    { headers: { Authorization: `Bearer ${localStorage.getItem('access')}` } }
  )

  data.images.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at))

  pavilion.value = data
  currentIndex.value = 0
}


async function savePavilion() {
  await axios.patch(
    `pavilions/${id.value}/`,
    pavilion.value,
    { headers: { Authorization: `Bearer ${localStorage.getItem('access')}` } }
  )
  alert('Данные сохранены')
}

async function saveImage(img) {
  await axios.patch(
    `images/${img.id}/`,
    { confirmed_state: img.confirmed_state },
    { headers: { Authorization: `Bearer ${localStorage.getItem('access')}` } }
  )
  await fetchPavilion()
}

async function deleteImage(imageId) {
  if (!confirm('Удалить изображение?')) return
  await axios.delete(
    `images/${imageId}/`,
    { headers: { Authorization: `Bearer ${localStorage.getItem('access')}` } }
  )
  await fetchPavilion()

  // Обновление индекса карусели
  if (currentIndex.value >= pavilion.value.images.length) {
    currentIndex.value = Math.max(0, pavilion.value.images.length - 1)
  }
}


function onNewImages(images) {
  newImages.value = images
}

async function uploadConfirmed() {
  const fd = new FormData()
  newImages.value.forEach(img => {
    fd.append('images', img.file)
    fd.append('confirmed_states', img.confirmed_state)
  })
  fd.append('pavilion', id.value)

  try {
    await axios.post(`images/upload/`, fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('access')}`
      }
    })
    newImages.value = []
    await fetchPavilion()
    alert('Новые изображения загружены')
  } catch (err) {
    console.error('Upload error:', err.response?.data || err)
    alert('Ошибка при загрузке изображений')
  }
}

watch(
  () => route.params.id,
  async newId => {
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



<style scoped>
.pavilion-edit {
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

/* Двухколоночная раскладка */
.edit-layout {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}
.edit-form,
.edit-carousel {
  background: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.edit-form {
  flex: 1 1 45%;
}
.edit-carousel {
  flex: 1 1 45%;
}

/* Секции формы */
.form-section h2 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}
.field input,
.field select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-family: inherit;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}
.field input:focus,
.field select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.3);
}

/* Кнопки действий формы */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
}
.form-actions button,
.form-actions a {
  font-size: 0.95rem;
  text-decoration: none;
}
.form-actions button {
  padding: 0.5rem 1rem;
  background: #10b981;
  color: #fff;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.2s;
}
.form-actions button:hover {
  background: #059669;
}

/* Карусель */
.carousel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carousel-image {
  width: 100%;
  max-height: 16rem;
  object-fit: contain;
  border-radius: 0.5rem;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.8);
  border: none;
  font-size: 1.5rem;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 9999px;
  transition: background 0.2s;
}
.carousel-btn:hover {
  background: rgba(255,255,255,1);
}
.prev { left: 0.5rem; }
.next { right: 0.5rem; }
.no-images {
  text-align: center;
  color: #9ca3af;
  padding: 4rem 0;
}

/* Метаданные фото */
.image-meta {
  margin-top: 1rem;
}
.image-meta p {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}
.image-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.image-actions button {
  flex: 1;
  padding: 0.5rem;
  font-size: 0.9rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  color: #fff;
}
.image-actions button:first-child {
  background: #f59e0b;
}
.image-actions button:last-child {
  background: #ef4444;
}
.image-actions button:first-child:hover {
  background: #d97706;
}
.image-actions button:last-child:hover {
  background: #dc2626;
}

/* Блок с загрузкой изображений */
.classifier-block {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.classifier-block .upload-label {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}
.classifier-block .upload-label input[type="file"] {
  display: none;
}

.classifier-block .file-list {
  margin-bottom: 1rem;
  font-size: 0.875rem;
}
.classifier-block .file-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}
.classifier-block .delete-btn {
  background: none;
  color: #ef4444;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}
.classifier-block .delete-btn:hover {
  color: #dc2626;
}

.classifier-block .primary-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.classifier-block .primary-btn:hover {
  background: #059669;
}

.classifier-block .image-preview {
  margin-top: 1.5rem;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  border-radius: 0.5rem;
}
.classifier-block .preview-img {
  width: 100%;
  height: 8rem;
  object-fit: cover;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}
.classifier-block .preview-meta {
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}
.classifier-block .select-state {
  width: 100%;
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #cbd5e1;
  margin-bottom: 0.5rem;
}
.classifier-block .classifier-upload-btn {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  margin-top: 1rem;
  cursor: pointer;
}
.classifier-block .classifier-upload-btn:hover {
  background: #2563eb;
}

</style>
