<template>
  <div class="game-panel">
    <!-- Barra superior -->
    <div v-if="!showLoginView" class="toolbar">
      <div class="left">
        <div class="search">
          <img src="/lupa.ico" class="search-icon" />
          <input v-model.trim="search" placeholder="Buscar juegos..." />
        </div>
        <div class="filters">
          <label for="order-select">Ordenar por:</label>
          <select id="order-select" v-model="sortOrder">
            <option value="asc">Año ascendente</option>
            <option value="desc">Año descendente</option>
          </select>
        </div>
      </div>
      <div class="right">
        <div class="auth-buttons" v-if="loggedIn">
          <button class="back-btn btn" @click="openAddModal">Añadir juego</button>
          <button class="back-btn btn" @click="imageModalOpen = true">Añadir imagen</button>
        </div>
        <div class="auth-controls">
          <button v-if="!loggedIn" class="back-btn btn" @click="showLoginView = true">Login</button>
          <button v-else class="back-btn btn" @click="logout">Logout</button>
        </div>
      </div>
    </div>

  <!-- Mensajes de error -->
  <div v-if="expiredMessage" class="alert alert--danger">{{ expiredMessage }}</div>
  <div v-if="fallbackMessage" class="alert alert--danger">{{ fallbackMessage }}</div>

    <!-- Vista de login -->
    <div v-if="showLoginView" class="auth-view">
      <div class="centered-login">
        <div class="login-form-inner">
          <LoginForm @logged-in="onLoggedIn" />
        </div>
      </div>
    </div>

    <!-- Vista principal -->
    <div v-else>

      <!-- Lista de juegos -->
      <div class="games">
        <template v-if="filteredAndSortedGames.length">
          <GameCard
            v-for="game in filteredAndSortedGames"
            :key="game.id"
            :game="game"
            :can-edit="loggedIn"
            @edit="onEdit(game)"
            @delete="onDelete(game)"
          />
        </template>
        <div v-else class="empty-state">
          <img src="/notfound.jpeg" class="empty-image" />
          <p>No se encontraron juegos.</p>
        </div>
      </div>
    </div>

    <!-- Modales -->
    <GameFormModal
      :open="modalOpen"
      :game="modalGame"
      @close="modalOpen = false"
      @saved="handleModalSaved"
    />
    <AddImageForm :open="imageModalOpen" @close="imageModalOpen = false" />
    <KeywordsFooter v-if="!showLoginView" :games="filteredAndSortedGames" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import api from '@/services/api'
import GameCard from './GameCard.vue'
import KeywordsFooter from './KeywordsFooter.vue'
import LoginForm from './LoginForm.vue'
import GameFormModal from './GameFormModal.vue'
import AddImageForm from './AddImageForm.vue'

// Variables reactivas
const search = ref('')
const sortOrder = ref('asc')
const games = ref([])
const loggedIn = ref(!!localStorage.getItem('access_token'))
const showLoginView = ref(false)
const modalOpen = ref(false)
const modalGame = ref(null)
const imageModalOpen = ref(false)
const expiredMessage = ref('')
const fallbackMessage = ref('')

// Carga inicial de juegos
async function loadGames() {
  try {
    const res = await api.get('/games?limit=1000')
    const normalizeImage = img => {
      if (!img) return null
      if (img.startsWith('http') || img.startsWith('/images/')) return img
      const parts = img.split('/')
      return `/images/${parts[parts.length - 1]}`
    }
    games.value = res.data.games.map(g => ({
      ...g,
      image: normalizeImage(g.image),
      year: Number(g.year || 0)
    }))
    fallbackMessage.value = ''
  } catch {
    fallbackMessage.value = 'No se pudo conectar al backend. Asegúrate de que está iniciado.'
  }
}

// Buscar + ordenar juegos
const filteredAndSortedGames = computed(() => {
  const q = search.value.toLowerCase()
  const filtered = games.value.filter(g =>
    g.name.toLowerCase().includes(q) || g.description.toLowerCase().includes(q)
  )
  return filtered.sort((a, b) =>
    sortOrder.value === 'asc'
      ? a.year - b.year
      : b.year - a.year
  )
})

// Login y logout
function onLoggedIn() {
  loggedIn.value = true
  showLoginView.value = false
  expiredMessage.value = ''
  loadGames()
}

function logout() {
  localStorage.removeItem('access_token')
  loggedIn.value = false
}

// Editar, añadir y eliminar juegos
function openAddModal() {
  modalGame.value = null
  modalOpen.value = true
}

function onEdit(game) {
  modalGame.value = game
  modalOpen.value = true
}

async function onDelete(game) {
  if (!confirm(`¿Eliminar "${game.name}"?`)) return
  try {
    await api.delete(`/games/${game.id}`)
    games.value = games.value.filter(g => g.id !== game.id)
  } catch (err) {
    alert(err.response?.data?.msg || 'Error al borrar el juego')
  }
}

function handleModalSaved(game) {
  const idx = games.value.findIndex(g => g.id === game.id)
  if (idx !== -1) games.value[idx] = game
  else games.value.unshift(game)
  modalOpen.value = false
}

// Detectar token expirado
function handleAuthExpired(e) {
  // Normalizar / traducir mensajes del backend a español
  const raw = (e.detail?.msg || '').toString()
  let userMsg = ''
  if (/missing authorization header/i.test(raw) || /missing authorization/i.test(raw) || /missing auth/i.test(raw)) {
    userMsg = 'Falta el encabezado de autorización (Authorization).'
  } else if (/token has expired/i.test(raw) || /token expired/i.test(raw) || /expired token/i.test(raw) || /token expir/i.test(raw)) {
    userMsg = 'El token ha expirado. Por favor, inicia sesión de nuevo.'
  } else if (raw) {
    // Si viene un mensaje en español ya, o cualquier otro texto, úsalo tal cual
    userMsg = raw
  } else {
    userMsg = 'El token ha expirado.'
  }

  expiredMessage.value = userMsg
  localStorage.removeItem('access_token')
  loggedIn.value = false
}

onMounted(() => {
  loadGames()
  window.addEventListener('auth-expired', handleAuthExpired)
})
onBeforeUnmount(() => {
  window.removeEventListener('auth-expired', handleAuthExpired)
})

</script>