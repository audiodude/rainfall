<script lang="ts">
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
      <button
        id="preview-site-button"
        @click="createPreview"
        :disabled="!readyForPreview"
        class="cursor-pointer mt-4 disabled:cursor-auto bg-blue-500 disabled:bg-blue-400 hover:bg-blue-700 disabled:hover:bg-blue-400 font-semibold text-white font-bold py-2 px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
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
    <p v-if="previewError" class="text-sm mt-2 text-red-600 dark:text-red-400">
      {{ previewError }}
    </p>
  </div>
</template>

<style></style>
