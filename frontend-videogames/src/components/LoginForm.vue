<template>
  <div class="login-form centered-login">
    <form @submit.prevent="login" class="login-form-inner">
      <input class="form-field" v-model="username" placeholder="Username" required />
      <input class="form-field" v-model="password" placeholder="Password" type="password" required />
      <div style="text-align:center"><button type="submit" class="back-btn">Log in</button></div>
    </form>
  <!-- errors are handled at GamePanel level -->
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
