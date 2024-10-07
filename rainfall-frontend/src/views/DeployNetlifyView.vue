<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { getCsrf } from '../helpers/cookie';

export default {
  data() {
    return {
      errors: [],
      hasNetlifyToken: false,
    };
  },
  async mounted() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (user) {
      // TODO: Replace with user.hasNetlfiyToken once Pinia store is updated.
      if (this.hasNetlifyToken) {
        this.$router.replace('/sites');
        return;
      }
    } else {
      this.$router.replace('/');
    }

    // const resp = await fetch('/api/v1/mastodon/errors');
    // if (resp.ok) {
    //   const data = await resp.json();
    //   this.errors = data['errors'];
    // }
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
    <h2 class="text-gray-900 dark:text-white text-2xl md:text-2xl font-extrabold mb-2">
      Host site on Netlify
    </h2>
    <p class="mt-4 w-full md:w-3/4">
      <a class="text-blue-500 hover:underline" href="https://www.netlify.com/">Netlfiy</a> will host
      your artist site for free. You can use this page to automatically deploy your site there,
      without having to download the ZIP file and upload it yourself. You must first
      <a class="text-blue-500 hover:underline" href="https://app.netlify.com/signup">Sign up</a> for
      a free Netlify account, or log in if you already have one.
    </p>
    <p class="mt-4 w-full md:w-3/4">
      When you click the "Connect to Netlify" button below, you will be brought to the Netlify
      website and asked to connect your Netlify account to Rainfall. After that, you will return to
      this page to deploy the site.
    </p>
    <form
      class="flex flex-col items-center md:items-start"
      action="/api/v1/mastodon/init"
      method="POST"
    >
      <button>Connect to Netlify</button>
      <div id="error-list" class="mt-2 mb-2 text-sm text-red-600 dark:text-red-400">
        <span v-for="error in errors">{{ error }}</span>
      </div>
      <button
        id="netlify-connect-button"
        class="cursor-pointer mx-auto md:mx-0 mt-4 w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Connect to Netlify
      </button>
      <button
        id="netlify-deploy-button"
        :disabled="!hasNetlifyToken"
        class="cursor-pointer mx-auto md:mx-0 mt-4 w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Deploy
      </button>
      <input type="hidden" name="_csrf_token" :value="getCsrf()" />
    </form>
  </div>
</template>
