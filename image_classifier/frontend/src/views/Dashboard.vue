<template>
  <div class="dashboard-wrapper">
    <h1 class="page-header">Аналитика по нарядам и состоянию павильонов</h1>

    <!-- ФИЛЬТРЫ -->
    <div class="filters">
      <input type="date" v-model="filters.date_from" />
      <input type="date" v-model="filters.date_to" />
      <select v-model="filters.district">
        <option value="">Все округа</option>
        <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>
      <select v-model="filters.region">
        <option value="">Все районы</option>
        <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>
      <select v-model="filters.confirmed_state">
        <option value="">Все классы</option>
        <option v-for="c in classChoices" :key="c" :value="c">{{ c }}</option>
      </select>
      <button @click="resetFilters" class="btn-reset">Сбросить фильтры</button>
    </div>

    <!-- ДИАГРАММЫ -->
    <div class="dashboard-grid">
      <div class="pie-card">
        <h2 class="card-title">Состояние павильонов</h2>
        <Doughnut v-if="chartData" :data="chartData" :options="chartData.options" />
      </div>

      <div class="right-panel">
        <div class="bar-card">
          <label class="checkbox">
            <input type="checkbox" v-model="filters.overdue"/>
            Только просроченные
          </label>
          <Bar v-if="barData" :data="barData" :options="barData.options" />
        </div>

        <div class="metrics">
          <div class="metrics-header">
            <span>Показатель</span>
            <span>Значение</span>
          </div>
          <div class="metrics-row">
            <span>Топ сотрудник</span>
            <span><strong>{{ shortName(metrics?.top_employee) || '—' }}</strong></span>
          </div>
          <div class="metrics-row">
            <span>Быстрее всех</span>
            <span><strong>{{ shortName(metrics?.fastest_employee) || '—' }}</strong></span>
          </div>
          <div class="metrics-row">
            <span>Среднее время выполнения</span>
            <span><strong>{{ metrics?.avg_completion_time || '—' }}</strong></span>
          </div>
          <div class="metrics-row">
            <span>Средняя просрочка</span>
            <span><strong>{{ metrics?.avg_overdue_days || 0 }} дн.</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'
import axios from 'axios'
import ChartDataLabels from 'chartjs-plugin-datalabels'

ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale, ChartDataLabels)

const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

const filters = ref({
  date_from: firstDay.toISOString().slice(0, 10),
  date_to: lastDay.toISOString().slice(0, 10),
  district: '',
  region: '',
  confirmed_state: '',
  overdue: '',
})


const classChoices = ['не требует ремонта', 'граффити', 'плановый ремонт', 'срочный ремонт']
const districts = ref([])
const regions = ref([])
const chartData = ref(null)
const barData = ref(null)
const metrics = ref(null)

function authHeader() {
  return {
    Authorization: `Bearer ${localStorage.getItem('access')}`
  }
}

function resetFilters() {
  filters.value = {
    date_from: firstDay.toISOString().slice(0, 10),
    date_to: lastDay.toISOString().slice(0, 10),
    district: '',
    region: '',
    confirmed_state: '',
    overdue: '',
  }
}

function shortName(fullName) {
  if (!fullName) return ''
  const parts = fullName.split(' ')
  if (parts.length < 2) return fullName
  return `${parts[0]} ${parts[1][0]}.` + (parts[2] ? `${parts[2][0]}.` : '')
}

async function fetchMeta() {
  const [dRes, rRes] = await Promise.all([
    axios.get('/districts/'),
    axios.get('/regions/')
  ])
  districts.value = dRes.data
  regions.value = rRes.data
}

async function loadMetrics() {
  const { data } = await axios.get('/stats/order-metrics/', {
    params: filters.value,
    headers: authHeader()
  })
  metrics.value = data
}

async function loadChartData() {
  if (!filters.value.date_from || !filters.value.date_to) return

  const params = {
    date_from: filters.value.date_from,
    date_to: filters.value.date_to,
    district: filters.value.district,
    region: filters.value.region,
    state: filters.value.confirmed_state,
    overdue: filters.value.overdue,
  }

  try {
    const [pieRes, barRes] = await Promise.all([
      axios.get('/stats/pavilion-states/', {params, headers: authHeader()}),
      axios.get('/stats/order-bar/', {params, headers: authHeader()})
    ])

    // === PIE CHART ===
    const pieLabels = Object.keys(pieRes.data)
    const pieValues = Object.values(pieRes.data).map(Number)
    const pieTotal = pieValues.reduce((acc, val) => acc + val, 0)

    chartData.value = {
      labels: pieLabels,
      datasets: [{
        label: 'Состояние',
        backgroundColor: ['#10b981', '#facc15', '#fb923c', '#ef4444'],
        data: pieValues
      }]
    }

    chartData.value.options = {
      plugins: {
        datalabels: {
          formatter: (value) =>
              pieTotal > 0 && value > 0 ? `${((value / pieTotal) * 100).toFixed(1)}%` : '',
          color: '#fff',
          font: {weight: 'bold'}
        }
      }
    }

    // === BAR CHART ===
    const isOverdue = filters.value.overdue === true || filters.value.overdue === 'true'
    const labels = barRes.data.map(x => x.name)
    const dataset1 = isOverdue
        ? barRes.data.map(x => x.overdue)
        : barRes.data.map(x => x.done)
    const dataset2 = barRes.data.map(x => x.total)

    const barTotalMap = {}
    barRes.data.forEach(row => {
      barTotalMap[row.name] = row.total
    })

    barData.value = {
      labels,
      datasets: [
        {
          label: isOverdue ? 'Просрочено' : 'Выполнено',
          backgroundColor: isOverdue ? '#f87171' : '#3b82f6',
          data: dataset1,
          barThickness: 28
        },
        {
          label: 'Всего нарядов',
          backgroundColor: '#d1d5db',
          data: dataset2,
          barThickness: 28
        }
      ]
    }

    barData.value.options = {
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const name = context.label
              const val = context.raw
              const total = barTotalMap[name] || val
              return `${val} из ${total}`
            }
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'end',
          formatter: (val, ctx) => {
            const name = ctx.chart.data.labels[ctx.dataIndex]
            const total = barTotalMap[name] || val
            return `${val}`
          },
          color: '#111827',
          font: {weight: 'bold', size: 12}
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: Math.max(...barRes.data.map(x => x.total)) + 1,
          ticks: {
            stepSize: 1
          }
        }
      }
    }

  } catch (e) {
    console.error('Ошибка при загрузке диаграмм:', e)
  }
}

onMounted(async () => {
  await fetchMeta()
  await loadChartData()
  await loadMetrics()
})

watch(filters, async () => {
  await loadChartData()
  await loadMetrics()
}, { deep: true })
</script>

<style scoped>
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
}

.page-header {
  font-size: 1.75rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: center;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.filters input,
.filters select {
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  min-width: 150px;
}

.btn-reset {
  padding: 0.5rem 1rem;
  background: #e5e7eb;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}
.btn-reset:hover {
  background: #d1d5db;
}

.dashboard-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.pie-card {
  flex: 1.3;
  min-width: 420px;
  background: #fff;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 0 4px rgba(0,0,0,0.05);
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 500px;
}

.bar-card {
  background: #fff;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 0 4px rgba(0,0,0,0.05);
}

.metrics {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metrics-header,
.metrics-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  font-weight: 500;
}

.metrics-header {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.25rem;
  margin-bottom: 0.25rem;
  color: #374151;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
</style>
