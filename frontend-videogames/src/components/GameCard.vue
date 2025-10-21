<template>
  <div class="game-card">
    <img :src="game.image" :alt="game.name" class="game-image"/>
    <h2>{{ game.name }}</h2>
    <p>{{ game.description }}</p>
    <p>Año: {{ game.year }}</p>
    <template v-if="game.playableComponent">
      <button type="button" class="play-btn" @click="emit('play', game)">
        Ver más
      </button>
    </template>
    <template v-else>
      <a :href="game.url" target="_blank">
        Ver más
      </a>
    </template>
  </div>
</template>

<script setup>
defineProps({
  game: { type: Object, required: true }
})
const emit = defineEmits(['play'])

</script>
