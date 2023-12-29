<script lang="ts">
import { getCsrf } from '../helpers/cookie';

export default {
  props: ['cardinality', 'siteId', 'readyForPreview'],
  data(): {
    previewError: string;
    previewUrl: undefined | string;
    previewLoading: boolean;
  } {
    return {
      previewError: '',
      previewUrl: undefined,
      previewLoading: false,
    };
  },
  created() {
    this.$emit('invalidate-preview', this.invalidatePreview);
  },
  methods: {
    async createPreview() {
      this.previewLoading = true;
      this.previewError = '';

      const csrfToken = await getCsrf();
      if (!csrfToken) {
        return;
      }
      const resp = await fetch(`/api/v1/preview/${this.siteId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
      });

      setTimeout(() => {
        this.previewLoading = false;
      }, 250);
      if (resp.ok) {
        this.previewUrl = `/preview/${this.siteId}`;
        this.$emit('preview-requested');
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
      this.previewError = '';
      this.previewUrl = undefined;
    },
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md flex flex-col md:flex-row items-center">
      <button
        id="preview-site-button"
        @click="createPreview"
        :disabled="!readyForPreview"
        class="cursor-pointer mt-4 w-10/12 md:w-32 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Preview Site
      </button>
      <div
        v-if="previewLoading || previewUrl || previewError"
        class="mt-4 md:ml-4"
        aria-live="polite"
      >
        <div v-if="previewLoading" class="preview-load">Loading preview...</div>
        <div v-if="!previewLoading && !previewError" class="preview-load">
          <a
            :href="previewUrl"
            target="_blank"
            class="preview-link font-medium text-blue-600 dark:text-blue-400 hover:underline"
            >Open preview in new window</a
          >
        </div>
      </div>
    </div>
    <p v-if="previewError" class="text-sm mt-2 text-red-600 dark:text-red-400">
      {{ previewError }}
    </p>
  </div>
</template>

<style></style>
