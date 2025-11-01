<template>
  <div>
    <h2>Agregar Usuario</h2>
    <form @submit.prevent="addUser">
      <input v-model="newUser.firstName" placeholder="Nombre" required />
      <input v-model="newUser.lastName" placeholder="Apellido" required />
      <input v-model="newUser.email" placeholder="Email" required />
      <button type="submit" :disabled="loading">{{ loading ? 'Enviando...' : 'Agregar' }}</button>
    </form>
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
      loading: false
    }
  },
  methods: {
    async addUser() {
      this.loading = true
      try {
        const created = await UsersService.addUser(this.newUser)
        console.log('Usuario creado:', created)
        this.$emit('user-added', created)
        this.newUser = { firstName: '', lastName: '', email: '' }
      } catch (err) {
        console.error('Error al crear usuario:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>