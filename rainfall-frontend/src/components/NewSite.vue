<script lang="ts">
import { getCsrf } from '../helpers/cookie';

export default {
  data() {
    return {
      createError: false,
      name: '',
    };
  },
  methods: {
    async createSite() {
      this.createError = false;
      const resp = await fetch('/api/v1/site', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({
          site: {
            name: this.name || 'My Cool Site',
          },
        }),
      });
      if (!resp.ok) {
        setTimeout(() => {
          this.createError = true;
        }, 250);
      }
      this.$emit('site-created');
    },
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md">
      <div>
        <label for="new-site" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
          >Site name</label
        >
        <input
          id="new-site"
          v-model="name"
          type="text"
          class="max-w-xl bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="My Cool Site"
          maxlength="255"
          required
        />
      </div>
      <button
        id="new-button"
        @click="createSite()"
        class="cursor-pointer mt-4 disabled:cursor-auto bg-blue-500 disabled:bg-blue-400 hover:bg-blue-700 disabled:hover:bg-blue-400 font-semibold text-white font-bold py-2 px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Create site
      </button>
      <p v-if="createError" class="text-sm text-red-600 dark:text-red-400">
        Something went wrong while creating your site.
      </p>
    </div>
  </div>
</template>

<style></style>
