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
import gamesData from '@/data/games.js'

const search = ref('')
const sortOrder = ref('asc')
// Emitimos 'play' hacia el padre
const emit = defineEmits(['play'])

const filteredAndSortedGames = computed(() => {
  const q = search.value.toLowerCase()
  const filtered = gamesData.filter(game =>
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
</script>
