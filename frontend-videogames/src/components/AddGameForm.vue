<template>
  <div class="add-game-form">
    <h3>{{ isEditing ? 'Editar juego' : 'Añadir juego' }}</h3>
    <form ref="formEl" @submit.prevent="submit">
  <input class="form-field" v-model="form.name" placeholder="Título" required />
  <input class="form-field" v-model.number="form.year" placeholder="Año" type="number" :min="MIN_YEAR" :max="MAX_YEAR" />
  <input class="form-field" v-model="form.url" placeholder="URL (opcional)" />
  <input class="form-field" v-model="form.image" placeholder="Imagen URL (opcional)" />
  <textarea class="form-field" v-model="form.description" placeholder="Descripción (opcional)"></textarea>
      <div style="display:flex; gap:8px; align-items:center; margin-top:8px">
        <button type="submit" :disabled="loading">{{ loading ? 'Enviando...' : (isEditing ? 'Guardar' : 'Añadir') }}</button>
        <button v-if="isEditing" type="button" @click="cancelEdit">Cancelar</button>
      </div>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { reactive, ref, watch, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  // optional game to edit
  game: { type: Object, default: null }
})

const emit = defineEmits(['game-added', 'game-updated', 'cancel-edit'])

const form = reactive({ name: '', year: null, url: '', image: '', description: '' })
const loading = ref(false)
const error = ref(null)
const MIN_YEAR = 1952
const MAX_YEAR = 2025
const formEl = ref(null)

const isEditing = computed(() => !!props.game)

// populate form when editing
watch(() => props.game, (g) => {
  if (g) {
    form.name = g.name || g.title || ''
    form.year = g.year || g.release_year || null
    form.url = g.url || ''
    form.image = g.image || ''
    form.description = g.description || ''
  } else {
    form.name = ''
    form.year = null
    form.url = ''
    form.image = ''
    form.description = ''
  }
}, { immediate: true })

async function submit() {
  error.value = null
  // Use native browser validation so the user sees the standard tooltip
  if (formEl.value && !formEl.value.reportValidity()) {
    return
  }
  loading.value = true
  try {
    const payload = { title: form.name }
    if (form.year) payload.release_year = form.year
    if (form.url) payload.url = form.url
    if (form.image) payload.image = form.image
    if (form.description) payload.description = form.description

    if (isEditing.value) {
      // update
      const res = await api.put(`/games/${props.game.id}`, payload)
      emit('game-updated', res.data)
    } else {
      const res = await api.post('/games', payload)
      emit('game-added', res.data)
      // clear form after create
      form.name = ''
      form.year = null
      form.url = ''
      form.image = ''
      form.description = ''
    }
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error al guardar juego'
  } finally {
    loading.value = false
  }
}

function cancelEdit() {
  emit('cancel-edit')
}
</script>
