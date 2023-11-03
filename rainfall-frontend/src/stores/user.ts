import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state() {
    return {
      user: null,
    };
  },
  getters: {
    isLoggedIn(state) {
      return !!state.user;
    },
  },
  actions: {
    async loadUser(force = false) {
      if (this.user && !force) {
        return;
      }
      const resp = await fetch('/api/v1/user');
      if (resp.ok) {
        this.user = await resp.json();
      }
    },
  },
});
