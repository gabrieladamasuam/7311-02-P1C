<template>
  <div v-if="open" class="modal-overlay" @click="onOverlayClick">
    <div class="modal-dialog" role="dialog" aria-modal="true" @click.stop>
      <header class="modal-header">
        <h3>{{ game ? 'Editar juego' : 'Añadir juego' }}</h3>
        <button class="close-btn" @click="close">✕</button>
      </header>
      <section class="modal-body">
        <AddGameForm :game="game" @game-added="onSaved" @game-updated="onSaved" @cancel-edit="close" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import AddGameForm from './AddGameForm.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  game: { type: Object, default: null }
})
const emit = defineEmits(['close', 'saved'])

function close() {
  emit('close')
}

function onSaved(game) {
  emit('saved', game)
  emit('close')
}

function onOverlayClick() {
  // clicking the overlay closes modal
  close()
}

// optional: when open, focus handled by AddGameForm's first input
watch(() => props.open, (v) => {
  // no-op placeholder if we want to add focus logic later
})

</script>