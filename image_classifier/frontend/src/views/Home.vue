<template>
  <section class="hero">
    <div class="hero-content">
      <h1>
        Контролируйте <span>павильоны</span> в один клик
      </h1>
      <p>
        Обзор, классификация и учёт обслуживания городских павильонов в едином интерфейсе.
      </p>
      <div class="quick-actions">
        <router-link to="/pavilions/create" class="card">
          <fa icon="building-columns" class="icon" />
          <h3>Новый павильон</h3>
          <p>Добавьте метаданные и фото</p>
        </router-link>
        <router-link to="/orders/create" class="card">
          <fa icon="clipboard-list" class="icon" />
          <h3>Создать наряд</h3>
          <p>Запланируйте ремонт</p>
        </router-link>
      </div>
    </div>

    <div class="hero-illustration">
      <img src="@/assets/pavilion.jpg" alt="Иллюстрация павильонов" />
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.hero {
  display: flex;
  gap: 5%;
  align-items: center;
  padding: 4rem 2rem;
}

.hero-content,
.hero-illustration {
  flex: 1 1 45%;
}

/* Заголовок */
.hero-content h1 {
  font-size: 3rem;
  line-height: 1.2;
  margin-bottom: 1rem;
}
.hero-content h1 span {
  color: #2563eb;
}

/* Описание */
.hero-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #555;
}

/* Быстрые действия */
.quick-actions {
  display: flex;
  gap: 2rem;
  margin-top: 3rem;
  justify-content: flex-start;
}

.card {
  flex: 1;
  max-width: 200px;
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}
.card:hover {
  transform: translateY(-4px);
}

.card .icon {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #2563eb;
}

.card h3 {
  margin-bottom: 0.5rem;
}

.card p {
  font-size: 0.9rem;
  color: #666;
}

/* Иллюстрация */
.hero-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
  /* Ограничиваем высоту контейнера иллюстрации */
  max-height: 500px;    /* или 70vh, если хотите 70% от высоты экрана */
  overflow: hidden;
}

.hero-illustration img {
  height: 500px;
  width: auto;
}

</style>
