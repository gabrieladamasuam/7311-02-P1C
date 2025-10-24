<template>
  <div class="game-card">
    <img :src="game.image" :alt="game.name" class="game-image"/>
    <h2>{{ game.name }}</h2>
    <p class="game-desc">{{ game.description }}</p>
    <p class="game-year">Año: {{ game.year }}</p>

    <div class="action-top">
      <template v-if="game.playableComponent">
        <button type="button" class="play-btn" @click="emit('play', game)">Ver más</button>
      </template>
      <template v-else>
        <a class="play-link" :href="game.url" target="_blank">Ver más</a>
      </template>
    </div>

    <div class="action-bottom" v-if="canEdit">
      <button class="edit-btn" type="button" @click="emit('edit', game)">Editar</button>
      <button class="delete-btn" type="button" @click="emit('delete', game)">Borrar</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  game: { type: Object, required: true },
  canEdit: { type: Boolean, default: false }
})
const emit = defineEmits(['play', 'edit', 'delete'])

</script>