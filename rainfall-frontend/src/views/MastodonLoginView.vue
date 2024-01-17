<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { getCsrf } from '../helpers/cookie';

export default {
  data() {
    return {
      host: null,
      errors: [],
      netloc: '',
    };
  },
  async mounted() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (user) {
      if (user.is_welcomed) {
        this.$router.replace('/sites');
        return;
      }
      this.$router.replace('/welcome');
      return;
    }
    const resp = await fetch('/api/v1/mastodon/errors');
    if (resp.ok) {
      const data = await resp.json();
      this.netloc = data['netloc'];
      this.errors = data['errors'];
    }
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    getCsrf() {
      return getCsrf();
    },
  },
};
</script>

<template>
  <div>
    <h1 class="text-gray-900 dark:text-white text-2xl md:text-2xl font-extrabold mb-2">
      Sign In with Mastodon
    </h1>
    <p class="mt-4 w-full md:w-3/4">
      To sign in with your Mastodon account, you must first enter the host where your instance is
      located (eg mastodon.social). You will then be sent to your home Mastodon instance where you
      can authorize the Rainfall app and continue to login.
    </p>
    <form
      class="flex flex-col items-center md:items-start"
      action="/api/v1/mastodon/init"
      method="POST"
    >
      <input
        type="text"
        name="host"
        v-model="netloc"
        placeholder="mastodon.social"
        class="block w-full md:w-3/4 p-4 mt-4 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 sm:text-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      />
      <div class="mt-2 mb-2 text-sm text-red-600 dark:text-red-400">
        <span v-for="error in errors">{{ error }}</span>
      </div>
      <button
        id="preview-site-button"
        class="cursor-pointer mx-auto md:mx-0 mt-4 w-10/12 md:w-32 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Sign in
      </button>
      <input type="hidden" name="_csrf_token" :value="getCsrf()" />
    </form>
  </div>
</template>
