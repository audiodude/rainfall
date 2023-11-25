<script lang="ts">
export default {
  props: ['cardinality', 'siteId', 'readyForPreview'],
  data(): {
    createError: boolean;
    previewError: string;
    previewUrl: undefined | string;
    previewLoading: boolean;
  } {
    return {
      createError: false,
      previewError: '',
      previewUrl: undefined,
      previewLoading: false,
    };
  },
  created() {
    this.$emit('invalidate-preview', this.invalidatePreview);
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
    async createPreview() {
      this.previewLoading = true;
      this.previewError = '';

      const resp = await fetch(`/api/v1/preview/${this.siteId}`, {
        method: 'POST',
      });

      setTimeout(() => {
        this.previewLoading = false;
      }, 250);
      if (resp.ok) {
        this.previewUrl = `/preview/${this.siteId}`;
        return;
      }

      let error = 'An unknown error occurred';
      if (resp.headers.get('Content-Type') == 'application/json') {
        const data = await resp.json();
        error = data.error;
      }
      setTimeout(() => {
        this.previewError = error;
      }, 250);
    },
    invalidatePreview() {
      console.log('invalidate called');
      this.previewError = '';
      this.previewUrl = undefined;
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
          class="cursor-pointer mt-4 disabled:cursor-auto bg-transparent hover:bg-blue-500 disabled:hover:bg-transparent font-semibold hover:text-white disabled:hover:dark:text-gray-300 py-2 px-4 border border-blue-500 hover:border-transparent disabled:hover:border-blue-500 rounded"
        >
          Add Release
        </button>
        <button
          id="preview-site-button"
          @click="createPreview"
          :disabled="!readyForPreview"
          class="cursor-pointer mt-4 md:ml-4 disabled:cursor-auto bg-transparent hover:bg-blue-500 disabled:hover:bg-transparent font-semibold hover:text-white disabled:hover:dark:text-gray-300 py-2 px-4 border border-blue-500 hover:border-transparent disabled:hover:border-blue-500 rounded"
        >
          Preview Site
        </button>
        <div
          v-if="previewLoading || previewUrl || previewError"
          class="mt-4 md:ml-4"
          aria-live="polite"
        >
          <div v-if="previewLoading">Loading preview...</div>
          <div v-if="!previewLoading && !previewError">
            <a
              :href="previewUrl"
              target="_blank"
              class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
              >Open preview in new window</a
            >
          </div>
        </div>
      </div>
      <p v-if="createError" class="text-sm mt-2 text-red-600 dark:text-red-400">
        Something went wrong while creating your release.
      </p>
      <p v-if="previewError" class="text-sm mt-2 text-red-600 dark:text-red-400">
        {{ previewError }}
      </p>
      <p></p>
    </div>
  </div>
</template>

<style></style>
