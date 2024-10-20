<script lang="ts">
import { getCsrf } from '../helpers/cookie';

export default {
  props: ['cardinality', 'siteId'],
  data(): {
    createError: boolean;
  } {
    return {
      createError: false,
    };
  },
  methods: {
    async createRelease() {
      this.createError = false;
      const resp = await fetch('/api/v1/release', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({
          release: {
            name: `Release ${this.cardinality}`,
            site_id: this.siteId,
          },
        }),
      });
      if (!resp.ok) {
        setTimeout(() => {
          this.createError = true;
        }, 250);
      }
      this.$emit('release-created');
    },
  },
};
</script>

<template>
  <div class="flex flex-col items-center mt-4 md:mt-0">
    <button
      id="new-release-button"
      @click="createRelease"
      class="cursor-pointer w-10/12 md:w-48 py-4 md:py-2 px-4 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-gray-200 disabled:text-gray-600 disabled:text-white disabled:bg-blue-400 hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white font-bold py-2 px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
    >
      Add Release
    </button>
    <p v-if="createError" class="text-sm mt-2 text-red-600 dark:text-red-400">
      Something went wrong while creating your release.
    </p>
  </div>
</template>

<style></style>
