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
      previewUrl: '',
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

      const resp = await fetch(`/api/v1/preview/${this.siteId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
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
  <div class="mt-4 block text-center md:text-left md:flex md:items-center">
    <button
      id="preview-site-button"
      @click="createPreview"
      :disabled="!readyForPreview"
      class="cursor-pointer w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
    >
      Preview Site
    </button>
    <div
      v-if="previewLoading || previewUrl || previewError"
      class="my-2 md:mb-0 text-center md:text-left md:mt-0 md:ml-4"
      aria-live="polite"
    >
      <div v-if="previewLoading" class="preview-load">
        <div role="status" class="w-16 m-auto">
          <svg
            aria-hidden="true"
            class="loader w-12 h-12 md:w-8 md:h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
            viewBox="0 0 100 101"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
              fill="currentColor"
            />
            <path
              d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
              fill="currentFill"
            />
          </svg>
          <span class="sr-only">Loading site preview...</span>
        </div>
      </div>
      <div
        v-if="!previewLoading && !previewError"
        Expand
        Down
        class="preview-load h-12 md:h-auto leading-[3rem] md:leading-none"
      >
        <a
          :href="previewUrl"
          target="_blank"
          class="preview-link font-medium text-blue-600 dark:text-blue-400 hover:underline"
          >Open preview in new window</a
        >
      </div>
    </div>
    <p v-if="previewError" class="text-sm mt-2 w-10/12 md:w-48 text-red-600 dark:text-red-400">
      {{ previewError }}
    </p>
  </div>
</template>

<style></style>
