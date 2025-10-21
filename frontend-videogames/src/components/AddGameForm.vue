<template>
  <div class="add-game-form">
    <h3>Añadir juego</h3>
    <form @submit.prevent="addGame">
      <input v-model="form.name" placeholder="Título" required />
      <input v-model.number="form.year" placeholder="Año" type="number" />
      <input v-model="form.url" placeholder="URL (opcional)" />
      <input v-model="form.image" placeholder="Imagen URL (opcional)" />
      <textarea v-model="form.description" placeholder="Descripción (opcional)"></textarea>
      <button type="submit" :disabled="loading">{{ loading ? 'Enviando...' : 'Añadir' }}</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '@/services/api'

const form = reactive({ name: '', year: null, url: '', image: '', description: '' })
const loading = ref(false)
const error = ref(null)
const emit = defineEmits(['game-added'])

async function addGame() {
  error.value = null
  loading.value = true
  try {
    const payload = { name: form.name }
    if (form.year) payload.year = form.year
    if (form.url) payload.url = form.url
    if (form.image) payload.image = form.image
    if (form.description) payload.description = form.description
    const res = await api.post('/games', payload)
    emit('game-added', res.data)
    form.name = ''
    form.year = null
    form.url = ''
    form.image = ''
    form.description = ''
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error al crear juego'
  } finally {
    loading.value = false
  }
}
</script>
