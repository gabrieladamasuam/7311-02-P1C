<template>
  <div class="login-form centered-login">
    <form class="login-form-inner" @submit.prevent="handleLogin">
      <input class="form-field" v-model="username" placeholder="Usuario" required/>
      <input class="form-field" v-model="password" type="password" placeholder="Contraseña" required/>

      <button type="submit" class="back-btn btn">Entrar</button>

      <p v-if="errorMsg" class="alert alert--danger" role="alert">
        {{ errorMsg }}
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

// Campos del formulario
const username = ref('')
const password = ref('')
const errorMsg = ref('')

const emit = defineEmits(['logged-in'])

// Maneja el inicio de sesión
async function handleLogin() {
  errorMsg.value = ''
  try {
    const res = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    })

    // Guarda el token JWT para las siguientes peticiones
    localStorage.setItem('access_token', res.data.access_token)

    // Notifica al componente padre que el usuario se ha logueado
    emit('logged-in')
  } catch (err) {
    errorMsg.value = err.response?.data?.msg || 'Error al iniciar sesión.'
  }
}
</script>