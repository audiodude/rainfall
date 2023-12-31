import { defineStore } from 'pinia';
import { type User } from '../types/user';
import { getCsrf } from '../helpers/cookie';

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

      if (!this.userPromise || force) {
        this.userPromise = fetch('/api/v1/user')
          .then((resp) => {
            if (resp.ok) {
              return resp.json();
            } else if (resp.status === 404) {
              // 404 properly indicates no logged in user.
              return null;
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
      const resp = await fetch('/api/v1/logout', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      });
      if (resp.ok) {
        this.user = null;
      }
    },
  },
});
