import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach token from localStorage if present
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: if we receive 401 (expired/invalid token), clear token and notify UI
api.interceptors.response.use(
  res => res,
  err => {
    const status = err.response?.status
    const msg = err.response?.data?.msg || err.message
    if (status === 401) {
      try {
        localStorage.removeItem('access_token')
      } catch (e) {
        // ignore
      }
      // Do not dispatch a global auth-expired for failed login attempts (they will
      // be handled locally by the LoginForm). Only dispatch for other endpoints.
      const requestUrl = err.config?.url || ''
      const isLogin = requestUrl.includes('/auth/login') || requestUrl.endsWith('/auth/login')
      if (!isLogin) {
        try {
          window.dispatchEvent(new CustomEvent('auth-expired', { detail: { msg } }))
        } catch (e) {
          // no-op in non-browser env
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api
