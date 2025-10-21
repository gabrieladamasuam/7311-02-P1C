<template>
  <footer class="keywords-footer">
    <template v-if="keywords.length">
      <span>Keywords: </span>
      <template v-for="(w, i) in keywords" :key="w">
        <strong class="keyword">{{ w }}</strong><span v-if="i < keywords.length - 1">, </span>
      </template>
    </template>
    <span v-else>No hay keywords comunes.</span>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  games: { type: Array, default: () => [] }
})

// Palabras comunes a TODOS los juegos visibles (simple e intuitivo)
function wordSet(game) {
  const text = ((game?.name || '') + ' ' + (game?.description || ''))
    .toLowerCase()
    .replace(/[.,!?;:()"']/g, ' ')
  return new Set(text.split(/\s+/).filter(w => w.length > 2))
}

const keywords = computed(() => {
  const list = Array.isArray(props.games) ? props.games : []
  if (list.length < 2) return []
  const sets = list.map(wordSet)
  let common = sets[0]
  for (let i = 1; i < sets.length; i++) {
    const next = new Set()
    for (const w of common) if (sets[i].has(w)) next.add(w)
    common = next
    if (!common.size) break
  }
  return [...common].sort()
})
</script>