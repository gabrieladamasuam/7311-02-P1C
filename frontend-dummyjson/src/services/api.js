import axios from 'axios'

const api = axios.create({
  baseURL: 'https://dummyjson.com'
})

export const UsersService = {
  getUsers(params = { limit: 10, skip: 0 }) {
    return api.get('/users', { params }).then(res => res.data)
  },
  addUser(data) {
    return api.post('/users/add', data).then(res => res.data)
  }
}

export default api
