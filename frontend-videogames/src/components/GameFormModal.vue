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

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.modal-dialog {
  width: min(760px, 96%);
  background: var(--color-background, #0f0f12);
  border-radius: 12px;
  box-shadow: 0 14px 40px rgba(0,0,0,0.6);
  padding: 16px;
  color: var(--color-text);
}
.modal-header { display:flex; align-items:center; justify-content:space-between; gap:12px }
.modal-header h3 { margin:0 }
.close-btn { background:transparent; border:none; font-size:1.1rem; cursor:pointer; color:var(--color-text) }
.modal-body { margin-top: 8px }
</style>
