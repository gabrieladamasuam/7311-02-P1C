<template>
  <div v-if="open" class="modal-overlay" @click="onOverlayClick">
    <div class="modal-dialog" role="dialog" aria-modal="true" @click.stop>
      <header class="modal-header">
        <h3>Añadir imagen</h3>
        <button class="close-btn" @click="close">✕</button>
      </header>
      <section class="modal-body">
        <form @submit.prevent="uploadImage">
          <input
            type="file"
            class="form-field"
            @change="onFileChange"
            accept="image/*"
            required
          />
          <div style="display:flex; gap:8px; align-items:center; margin-top:8px;">
            <button class="back-btn" type="submit" :disabled="loading">
              {{ loading ? 'Subiendo...' : 'Subir imagen' }}
            </button>
          </div>
        </form>

        <p v-if="successMsg" style="color: lightgreen; margin-top: 8px;">
          {{ successMsg }}
        </p>
        <p v-if="errorMsg" style="color: red; margin-top: 8px;">
          {{ errorMsg }}
        </p>

        <div v-if="imageUrl" style="margin-top: 10px; text-align: center;">
          <img
            :src="imageUrl"
            alt="Vista previa"
            style="max-width: 180px; border-radius: 8px; margin-bottom: 6px;"
          />
          <p style="font-size: 0.9rem;">
            Ruta de imagen: <code>{{ imageUrl }}</code>
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const props = defineProps({
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const file = ref(null)
const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const imageUrl = ref('')

function onFileChange(e) {
  file.value = e.target.files[0]
}

function close() {
  emit('close')
  // limpiamos todo el estado del formulario
  file.value = null
  loading.value = false
  successMsg.value = ''
  errorMsg.value = ''
  imageUrl.value = ''
}

function onOverlayClick() {
  close()
}

async function uploadImage() {
  if (!file.value) {
    errorMsg.value = 'Selecciona una imagen primero.'
    return
  }

  loading.value = true
  successMsg.value = ''
  errorMsg.value = ''
  imageUrl.value = ''

  const formData = new FormData()
  formData.append('image', file.value)

  try {
    const res = await api.post('/add_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    successMsg.value = res.data.msg || 'Imagen subida correctamente'
    imageUrl.value = res.data.image_url
  } catch (err) {
    errorMsg.value =
      err.response?.data?.msg || 'Error al subir la imagen. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}
</script>
