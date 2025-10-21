<template>
  <div>
    <h2>Agregar Usuario</h2>
    <form @submit.prevent="addUser">
      <input v-model="newUser.firstName" placeholder="Nombre" required />
      <input v-model="newUser.lastName" placeholder="Apellido" required />
      <input v-model="newUser.email" placeholder="Email" required />
      <button type="submit" :disabled="loading">{{ loading ? 'Enviando...' : 'Agregar' }}</button>
    </form>
    <p v-if="error" style="color: red; margin-top: 8px">{{ error }}</p>
  </div>
</template>

<script>
import { UsersService } from '../services/api'

export default {
  data() {
    return {
      newUser: {
        firstName: '',
        lastName: '',
        email: ''
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async addUser() {
      this.error = null
      if (!this.newUser.firstName || !this.newUser.lastName || !this.newUser.email) {
        this.error = 'Todos los campos son obligatorios.'
        return
      }
      this.loading = true
      try {
  const created = await UsersService.addUser(this.newUser)
  console.log('Usuario creado:', created)
  this.$emit('user-added', created) // envía el usuario al padre (App.vue)
        this.newUser = { firstName: '', lastName: '', email: '' }
      } catch (err) {
        console.error('Error al crear usuario:', err)
        if (err.response && err.response.data) {
          this.error = err.response.data.message || 'Error al crear usuario.'
        } else {
          this.error = 'Error de red o servidor.'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
