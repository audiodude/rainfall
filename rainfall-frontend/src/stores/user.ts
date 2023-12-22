import { defineStore } from 'pinia';
import { type User } from '../types/user';

export const useUserStore = defineStore('user', {
  state(): { user: User | null; userPromise: Promise<User | null> | null } {
    return {
      user: null,
      userPromise: null,
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
        return this.user;
      }

      if (!this.userPromise) {
        this.userPromise = fetch('/api/v1/user')
          .then((resp) => {
            if (resp.ok) {
              return resp.json();
            }
            throw new Error(`Could not load user, response status=${resp.status}`);
          })
          .then((userData) => {
            this.user = userData;
            return this.user;
          });
      }
      return this.userPromise;
    },
    async signOut() {
      const resp = await fetch('/api/v1/logout');
      if (resp.ok) {
        this.user = null;
      }
    },
  },
});
