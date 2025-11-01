import axios from 'axios'

// Crea una instancia de Axios con la URL base del backend Flask
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: { 'Content-Type': 'application/json' }
})

// Antes de cada petición, añade el token si existe
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Si el backend devuelve error 401 (token inválido o expirado)
api.interceptors.response.use(
  res => res,
  err => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('access_token')
      const isLoginRequest = err.config?.url?.includes('/auth/login')
      // Notifica al resto de la app que el token ha caducado (excepto en el login)
      if (!isLoginRequest) {
        window.dispatchEvent(new CustomEvent('auth-expired', {
          detail: { msg: err.response?.data?.msg || 'Token expirado' }
        }))
      }
    }
    return Promise.reject(err)
  }
)

export default api

