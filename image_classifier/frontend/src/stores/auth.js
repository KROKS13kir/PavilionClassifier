import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  actions: {
    login(access, refresh) {
      this.token = access
      this.refresh = refresh
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
    },
    logout() {
      this.token = null
      this.refresh = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      delete axios.defaults.headers.common['Authorization']
    },
    initialize() {
      const token = localStorage.getItem('access')
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        this.token = token
        this.refresh = localStorage.getItem('refresh')
      }
    }
  }
})
