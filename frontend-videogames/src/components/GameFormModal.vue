<template>
  <div v-if="open" class="modal-overlay" @click="close">
    <div class="modal-dialog" role="dialog" aria-modal="true" @click.stop>
      <header class="modal-header">
        <h3>{{ isEditing ? 'Editar juego' : 'Añadir juego' }}</h3>
        <button class="close-btn" @click="close">✕</button>
      </header>

      <section class="modal-body">
        <form ref="formEl" @submit.prevent="handleSubmit" class="add-game-form">
          <input class="form-field" v-model="form.name" placeholder="Título" required />
          <input class="form-field" v-model.number="form.year" type="number" min="1952" max="2025" placeholder="Año" />

          <input class="form-field" v-model="form.image" placeholder="Ruta de imagen (debe haberse subido previamente)" required />

          <input class="form-field" v-model="form.url" type="url" placeholder="URL del juego" required />

          <textarea class="form-field" v-model="form.description" placeholder="Descripción (opcional)"></textarea>

          <button class="back-btn btn" type="submit" :disabled="loading">
            {{ loading ? 'Enviando...' : (isEditing ? 'Guardar' : 'Añadir') }}
          </button>
        </form>

        <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  open: { type: Boolean, default: false },
  game: { type: Object, default: null }
})

const emit = defineEmits(['close', 'saved'])

const form = reactive({ name: '', year: null, description: '', image: '', url: '' })
const loading = ref(false)
const errorMsg = ref('')
const formEl = ref(null)

const isEditing = computed(() => !!props.game)

watch(() => props.game, (g) => {
  if (g) Object.assign(form, g)
  else Object.assign(form, { name: '', year: null, description: '', image: '', url: '' })
}, { immediate: true })

function close() {
  emit('close')
  errorMsg.value = ''
  loading.value = false
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!formEl.value?.reportValidity()) return

  loading.value = true
  try {
    // En producción solo permitimos imágenes locales (no URLs externas)
    if (form.image && (form.image.startsWith('http://') || form.image.startsWith('https://'))) {
      throw new Error('Solo se permiten imágenes locales. Sube la imagen desde el modal "Añadir imagen" y usa el nombre de fichero o /images/<archivo>.')
    }

    // Normalizar la ruta de imagen: aceptar tanto "archivo.png" como "/images/archivo.png"
    const imgName = form.image ? form.image.split('/').pop() : ''
    const payload = { ...form, image: imgName ? `/images/${imgName}` : '' }

    const res = isEditing.value
      ? await api.put(`/games/${props.game.id}`, payload)
      : await api.post('/games', payload)

    emit('saved', res.data)

    close()
  } catch (err) {
    errorMsg.value = err.response?.data?.msg || 'Error al guardar el juego'
  } finally {
    loading.value = false
  }
}
</script>