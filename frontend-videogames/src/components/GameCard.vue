<template>
  <div class="game-card">
    <img :src="game.image" :alt="game.name" class="game-image"/>
    <h2>{{ game.name }}</h2>
    <p class="game-desc">{{ game.description }}</p>
    <p class="game-year">Año: {{ game.year }}</p>

    <div class="action-top">
      <a class="play-link" :href="game.url || '#'" target="_blank" rel="noopener">Ver más</a>
    </div>

    <div class="action-bottom" v-if="canEdit">
      <button class="edit-btn btn" type="button" @click="emit('edit', game)">Editar</button>
      <button class="delete-btn btn" type="button" @click="emit('delete', game)">Borrar</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  game: { type: Object, required: true },
  canEdit: { type: Boolean, default: false }
})

const emit = defineEmits(['edit', 'delete'])

</script>