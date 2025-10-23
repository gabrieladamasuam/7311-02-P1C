<template>
  <div class="login-form centered-login">
    <form @submit.prevent="login" class="login-form-inner">
      <input class="form-field" v-model="username" placeholder="Username" required />
      <input class="form-field" v-model="password" placeholder="Password" type="password" required />
      <div style="text-align:center">
        <button type="submit" class="back-btn">Log in</button>
      </div>
      <!-- show a single prominent inline error directly under the button -->
      <div v-if="error" class="login-error" role="alert">{{ error }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const username = ref('')
const password = ref('')
const error = ref(null)
const emit = defineEmits(['logged-in', 'login-error'])

async function login() {
  error.value = null
  try {
    const res = await api.post('/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('access_token', res.data.access_token)
    emit('logged-in')
  } catch (err) {
    error.value = err.response?.data?.msg || 'Login failed'
    // also inform parent so it can show other global UI if needed
    emit('login-error', error.value)
  }
}
</script>

<style scoped>
.login-error {
  color: #fff;
  background: hsl(350, 60%, 35%); /* same as delete button */
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 12px;
  font-weight: 600;
  text-align: center;
}
</style>
