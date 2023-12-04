<script lang="ts">
export default {
  props: ['cardinality', 'siteId', 'readyForPreview'],
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
  <div>
    <div class="md:max-w-screen-md">
      <div class="flex flex-col md:flex-row items-center">
        <button
          id="new-release-button"
          @click="createRelease"
          class="cursor-pointer mt-4 disabled:cursor-auto bg-blue-500 hover:bg-blue-700 disabled:hover:bg-transparent font-semibold text-white font-bold py-2 px-4 border border-blue-500 rounded hover:text-white disabled:hover:dark:text-gray-300 hover:border-transparent disabled:hover:border-blue-500"
        >
          Add Release
        </button>
      </div>
      <p v-if="createError" class="text-sm mt-2 text-red-600 dark:text-red-400">
        Something went wrong while creating your release.
      </p>
    </div>
  </div>
</template>

<style></style>
