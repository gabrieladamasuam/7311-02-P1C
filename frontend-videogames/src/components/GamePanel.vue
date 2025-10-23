<template>
  <div class="game-panel">
  <div v-if="!showLoginView" class="toolbar">
      <div class="left">
        <div class="search">
          <img src="/lupa.ico" class="search-icon" />
          <input v-model.trim="search" placeholder="Buscar juegos..."/>
        </div>
        <div class="filters">
          <label for="order-select">Filtrar por:</label>
          <select id="order-select" v-model="sortOrder">
            <option value="asc">Año ascendente</option>
            <option value="desc">Año descendente</option>
          </select>
          <div style="margin-left:8px">
            <button v-if="!loggedIn" class="back-btn" type="button" @click="showLoginView = true">Login</button>
            <button v-else class="back-btn" type="button" @click="logout">Logout</button>
          </div>
        </div>
      </div>
      
    </div>
  <div v-if="expiredMessage" style="color: red; margin-bottom:8px">{{ expiredMessage }}</div>
  <div v-if="fallbackMessage" style="color: #a0a0a0; margin-bottom:8px">{{ fallbackMessage }}</div>

    <div v-if="showLoginView" class="auth-view">
      <div class="centered-login">
        <div class="login-form-inner">
          <LoginForm @logged-in="onLoggedIn" />
        </div>
      </div>
    </div>

  <div v-else>
      <div class="auth-area" style="margin: 12px 0">
        <template v-if="loggedIn">
          <div style="display:flex; gap:8px; align-items:center">
            <button class="back-btn" type="button" @click="openAddModal">Añadir juego</button>
          </div>
        </template>
        <template v-else>
        </template>
      </div>
    <div class="games">
      

      <template v-if="filteredAndSortedGames.length">
        <GameCard
          v-for="game in filteredAndSortedGames"
          :key="game.id"
          :game="game"
          :can-edit="loggedIn"
          @play="onPlay"
          @edit="onEdit"
          @delete="onDelete"
        />
      </template>
      <div v-else class="empty-state">
        <img src="/notfound.jpeg" class="empty-image" />
        <p>No se encontraron juegos.</p>
      </div>
    </div>
  </div>
  <GameFormModal :open="modalOpen" :game="modalGame" @close="modalOpen = false" @saved="handleModalSaved" />
  <KeywordsFooter v-if="!showLoginView" :games="filteredAndSortedGames" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import GameCard from './GameCard.vue'
import KeywordsFooter from './KeywordsFooter.vue'
import api from '@/services/api'
import LoginForm from './LoginForm.vue'
import AddGameForm from './AddGameForm.vue'
import GameFormModal from './GameFormModal.vue'
import localGames from '@/data/games.js'

const search = ref('')
const sortOrder = ref('asc')
// Emitimos 'play' hacia el padre
const emit = defineEmits(['play'])

const games = ref([])
const editingGame = ref(null)
const modalOpen = ref(false)
const modalGame = ref(null)
const fallbackMessage = ref('')
const showLoginView = ref(false)
const showDebug = ref(false)

async function loadGames() {
  // Always start with local bundle so it's visible even if backend is empty/unreachable
  const mapLocal = localGames.map(g => ({
    id: g.id != null ? Number(g.id) : null,
    name: g.name || '',
    description: g.description || '',
    year: Number(g.year || 0),
    image: g.image,
    url: g.url,
    playableComponent: g.playableComponent,
    localOnly: true
  }))
  // use a map keyed by id when available, otherwise by name (to avoid duplicates when name changes)
  const merged = new Map()
  mapLocal.forEach(g => {
    const key = g.id != null ? `id:${g.id}` : `name:${g.name}`
    merged.set(key, g)
  })

  try {
    const res = await api.get('/games')
    if (res.data && Array.isArray(res.data.games)) {
      res.data.games.forEach(g => {
        const item = {
          id: g.id != null ? Number(g.id) : null,
          name: (g.name || g.title || '') + '',
          description: g.description || '',
          year: Number(g.year || g.release_year || 0),
          image: g.image,
          url: g.url,
          playableComponent: g.playableComponent,
          localOnly: false
        }
        const key = item.id != null ? `id:${item.id}` : `name:${item.name}`
        merged.set(key, item)
      })
      fallbackMessage.value = ''
    } else {
      fallbackMessage.value = 'Mostrando juegos locales (backend no devolvió juegos)'
    }
  } catch (err) {
    console.error('Error loading games:', err)
    fallbackMessage.value = 'No se pudo conectar al backend — mostrando juegos locales'
  }

  // convert merged map to array and normalize ids to Number when possible
  games.value = Array.from(merged.values()).map(it => ({
    id: it.id != null ? Number(it.id) : undefined,
    name: it.name,
    description: it.description,
    year: Number(it.year || 0),
    image: it.image,
    url: it.url,
    playableComponent: it.playableComponent,
    localOnly: !!it.localOnly
  }))

  // Debug: log loaded game names in dev mode to help diagnose missing entries
  try {
    if (import.meta.env.DEV) {
      console.log('Loaded games:', games.value.map(g => ({ id: g.id, name: g.name, localOnly: g.localOnly })))
    }
  } catch (e) {
    // ignore when import.meta not available in some environments
  }
}

loadGames()

  const filteredAndSortedGames = computed(() => {
  const q = (search.value || '').toLowerCase()
  const filtered = games.value.filter(game =>
    (game.name || '').toLowerCase().includes(q) ||
    (game.description || '').toLowerCase().includes(q)
  )
  return filtered.sort((a, b) =>
    sortOrder.value === 'asc'
      ? (Number(a.year || 0) - Number(b.year || 0))
      : (Number(b.year || 0) - Number(a.year || 0))
  )
})

function onPlay(game) {
  emit('play', game)
}

const loggedIn = ref(!!localStorage.getItem('access_token'))
const expiredMessage = ref('')

function handleAuthExpired(e) {
  expiredMessage.value = e?.detail?.msg || 'Token has expired'
  // clear state
  try { localStorage.removeItem('access_token') } catch (e) {}
  loggedIn.value = false
  editingGame.value = null
}

onMounted(() => {
  window.addEventListener('auth-expired', handleAuthExpired)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth-expired', handleAuthExpired)
})

// When a user logs in, close the login view and reload games
function onLoggedIn() {
  loggedIn.value = true
  clearExpired()
  showLoginView.value = false
  loadGames()
}

// Clear expired message when user logs in or starts editing
function clearExpired() {
  expiredMessage.value = ''
}



function onGameAdded(game) {
  games.value.unshift({
    id: game.id,
    name: game.name || game.title,
    description: game.description || '',
    year: game.year || game.release_year,
    image: game.image,
    url: game.url
  })
}

function onGameUpdated(game) {
  // find and replace
  const idx = games.value.findIndex(g => g.id === game.id)
  const updated = {
    id: game.id,
    name: game.name || game.title,
    description: game.description || '',
    year: game.year || game.release_year,
    image: game.image,
    url: game.url
  }
  if (idx !== -1) games.value.splice(idx, 1, updated)
  editingGame.value = null
}

function cancelEdit() {
  editingGame.value = null
  clearExpired()
}

async function onDelete(game) {
  try {
    if (!confirm(`Eliminar juego "${game.name}"?`)) return
    await api.delete(`/games/${game.id}`)
    // remove locally
    const idx = games.value.findIndex(g => g.id === game.id)
    if (idx !== -1) games.value.splice(idx, 1)
  } catch (err) {
    console.error('Error deleting game:', err)
    alert(err.response?.data?.msg || 'Error al borrar juego')
  }
}

function onEdit(game) {
  // open modal to edit the game
  modalGame.value = game
  modalOpen.value = true
  clearExpired()
}

function openAddModal() {
  modalGame.value = null
  modalOpen.value = true
}

function handleModalSaved(game) {
  // if game has id and exists, update; else add
  if (!game) return
  const newId = Number(game.id)
  const idx = games.value.findIndex(g => Number(g.id) === newId)
  const updatedObj = {
    id: newId,
    name: game.name || game.title,
    description: game.description || '',
    year: game.year || game.release_year,
    image: game.image,
    url: game.url
  }
  if (idx !== -1) {
    games.value.splice(idx, 1, updatedObj)
  } else {
    games.value.unshift(updatedObj)
  }
  modalOpen.value = false
}

function logout() {
  try { localStorage.removeItem('access_token') } catch (e) {}
  loggedIn.value = false
  editingGame.value = null
  clearExpired()
}


</script>
