<template>
  <div class="game-panel">
    <div class="toolbar">
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
      </div>
    </div>
    <div class="auth-area" style="margin: 12px 0">
      <template v-if="!loggedIn">
        <LoginForm @logged-in="onLoggedIn" />
      </template>
      <template v-else>
        <AddGameForm @game-added="onGameAdded" />
      </template>
    </div>
    <div class="games">
      <template v-if="filteredAndSortedGames.length">
        <GameCard
          v-for="game in filteredAndSortedGames"
          :key="game.id"
          :game="game"
          @play="onPlay"
        />
      </template>
      <div v-else class="empty-state">
        <img src="/notfound.jpeg" class="empty-image" />
        <p>No se encontraron juegos.</p>
      </div>
    </div>
    <KeywordsFooter :games="filteredAndSortedGames" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import GameCard from './GameCard.vue'
import KeywordsFooter from './KeywordsFooter.vue'
import api from '@/services/api'
import LoginForm from './LoginForm.vue'
import AddGameForm from './AddGameForm.vue'

const search = ref('')
const sortOrder = ref('asc')
// Emitimos 'play' hacia el padre
const emit = defineEmits(['play'])

const games = ref([])

async function loadGames() {
  try {
    const res = await api.get('/games')
    // server returns { total, games: [...] }
    games.value = res.data.games.map(g => ({
      id: g.id,
      name: g.name || g.title,
      description: g.description || '',
      year: g.year || g.release_year,
      image: g.image,
      url: g.url
    }))
  } catch (err) {
    console.error('Error loading games:', err)
  }
}

loadGames()

const filteredAndSortedGames = computed(() => {
  const q = search.value.toLowerCase()
  const filtered = games.value.filter(game =>
    game.name.toLowerCase().includes(q) ||
    (game.description || '').toLowerCase().includes(q)
  )
  return filtered.sort((a, b) =>
    sortOrder.value === 'asc' ? a.year - b.year : b.year - a.year
  )
})

function onPlay(game) {
  emit('play', game)
}

const loggedIn = ref(!!localStorage.getItem('access_token'))

function onLoggedIn() {
  loggedIn.value = true
  loadGames()
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
</script>
