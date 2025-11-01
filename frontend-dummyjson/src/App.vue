<template>
  <div id="app">
    <h1>Usuarios DummyJSON</h1>
    <AddUserForm @user-added="addUserToList" />
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
    return { users: [] }
  },
  async mounted() {
    try {
      const data = await UsersService.getUsers({ limit: 150 })
      this.users = data.users
    } catch (err) {
      console.error('Error al obtener usuarios:', err)
    }
  },
  methods: {
    addUserToList(user) {
      this.users.unshift(user)
    }
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