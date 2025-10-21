<template>
  <div id="app">
    <h1>Usuarios DummyJSON</h1>
    <AddUserForm @user-added="addUserToList" />

    <div style="margin: 12px 0">
      <button @click="prevPage" :disabled="page === 0">Anterior</button>
      <span style="margin: 0 8px">Página: {{ page + 1 }}</span>
      <button @click="nextPage" :disabled="(page + 1) * limit >= total">Siguiente</button>
    </div>

    <UserList :users="users" />
  </div>
</template>

<script>
import AddUserForm from './components/AddUserForm.vue'
import UserList from './components/UserList.vue'
import { UsersService } from './services/api'

export default {
  components: { AddUserForm, UserList },
  data() {
    return {
      users: [],
      page: 0,
      limit: 10,
      total: 0
    }
  },
  methods: {
    async fetchUsers() {
      try {
        // dummyjson supports limit and skip for pagination
        const skip = this.page * this.limit
        const data = await UsersService.getUsers({ limit: this.limit, skip })

        // Merge any locally created users (persisted in localStorage) when on the first page
        const created = JSON.parse(localStorage.getItem('createdUsers') || '[]')
        if (this.page === 0 && created.length > 0) {
          // prepend created users and then the fetched users (avoid duplicates by id if possible)
          const ids = new Set(created.map(u => u.id))
          const fetched = data.users.filter(u => !ids.has(u.id))
          this.users = [...created, ...fetched].slice(0, this.limit)
        } else {
          this.users = data.users
        }
        this.total = data.total || 0
      } catch (err) {
        console.error('Error al obtener usuarios:', err)
      }
    },
    addUserToList(newUser) {
      // prepend the newly created user locally
      this.users.unshift(newUser)
      // keep list size reasonable
      if (this.users.length > this.limit) this.users.pop()
      this.total += 1
      // persist created users so they survive pagination/refresh
      const created = JSON.parse(localStorage.getItem('createdUsers') || '[]')
      created.unshift(newUser)
      localStorage.setItem('createdUsers', JSON.stringify(created))
    },
    nextPage() {
      if ((this.page + 1) * this.limit < this.total) {
        this.page += 1
        this.fetchUsers()
      }
    },
    prevPage() {
      if (this.page > 0) {
        this.page -= 1
        this.fetchUsers()
      }
    }
  },
  mounted() {
    this.fetchUsers()
  }
}
</script>

<style>
body {
  font-family: Arial, sans-serif;
  padding: 20px;
}
input {
  margin-right: 5px;
}
button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}
button:hover {
  background-color: #45a049;
}
</style>