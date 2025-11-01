<template>
  <footer class="keywords-footer">
    <template v-if="keywords.length">
      <span>Palabras comunes: </span>
      <template v-for="(word, i) in keywords" :key="word">
        <strong class="keyword">{{ word }}</strong><span v-if="i < keywords.length - 1">, </span>
      </template>
    </template>
    <span v-else>No hay palabras comunes.</span>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  games: { type: Array, default: () => [] }
})

// Convierte nombre y descripción de un juego en un conjunto (Set) de palabras
function wordSet(game) {
  const text = ((game?.name || '') + ' ' + (game?.description || ''))
    .toLowerCase()
    .replace(/[.,!?;:()"']/g, ' ')
  return new Set(text.split(/\s+/).filter(w => w.length > 2))
}

// Calcula las palabras comunes a todos los juegos visibles
const keywords = computed(() => {
  const list = props.games || []
  if (list.length < 2) return []

  let common = wordSet(list[0])

  // Comparamos con los demás juegos
  for (let i = 1; i < list.length; i++) {
    const current = wordSet(list[i])
    common = new Set([...common].filter(w => current.has(w)))
    if (common.size === 0) break
  }

  return [...common].sort()
})
</script>
