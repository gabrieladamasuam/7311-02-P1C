import axios from 'axios'

const api = axios.create({
  baseURL: 'https://dummyjson.com',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 5000
})

/**
 * Users helper methods kept here so there's a single service file (as requested).
 * These methods return `res.data` to match the previous `UsersService` behavior.
 */
const UsersService = {
  async getUsers({ limit = 10, skip = 0 } = {}) {
    const res = await api.get('/users', { params: { limit, skip } })
    return res.data
  },

  async addUser(data) {
    const res = await api.post('/users/add', data)
    return res.data
  }
}

export { UsersService }

export default api