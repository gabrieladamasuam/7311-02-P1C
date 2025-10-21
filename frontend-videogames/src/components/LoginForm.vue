<template>
  <div class="login-form">
    <h3>Login</h3>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" required />
      <input v-model="password" placeholder="Password" type="password" required />
      <button type="submit">Log in</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const username = ref('')
const password = ref('')
const error = ref(null)
const emit = defineEmits(['logged-in'])

async function login() {
  error.value = null
  try {
    const res = await api.post('/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('access_token', res.data.access_token)
    emit('logged-in')
  } catch (err) {
    error.value = err.response?.data?.msg || 'Login failed'
  }
}
</script>
