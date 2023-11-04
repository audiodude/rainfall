import { defineStore } from 'pinia';

export declare interface User {
  name: string;
  email: string;
  picture_url: string;
  is_welcomed: boolean;
}

export const useUserStore = defineStore('user', {
  state(): { user: User | null } {
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
    async signOut() {
      const resp = await fetch('/api/v1/logout');
      if (resp.ok) {
        this.user = null;
      }
    },
  },
});
