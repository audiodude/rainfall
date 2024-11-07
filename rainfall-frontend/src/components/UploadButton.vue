<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import { getCsrf } from '../helpers/cookie';

export default defineComponent({
  props: {
    uploadUrl: { type: String, required: true },
    paramName: { type: String, required: true },
    acceptFiles: { type: Array<String>, required: true },
  },
  data(): { files: FileList | null; fileError: string | null; loading: boolean } {
    return {
      files: null,
      fileError: null,
      loading: false,
    };
  },
  methods: {
    async upload() {
      if (!this.files) {
        return;
      }

      this.loading = true;
      this.fileError = null;

      let formData = new FormData();
      for (const song of this.files) {
        formData.append(this.paramName, song);
      }

      const resp = await fetch(this.uploadUrl, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
        body: formData,
      });
      this.loading = false;

      if (resp.ok) {
        this.files = null;
        this.fileInput.value = '';
        this.$emit('song-uploaded');
        return;
      }

      let error = 'An unknown error occurred';
      if (resp.status == 413) {
        error = 'That file is too large (> 100 MB)';
      }

      if (resp.headers.get('Content-Type') == 'application/json') {
        const data = await resp.json();
        error = data.error;
      }
      setTimeout(() => {
        this.fileError = error;
      }, 250);
    },
    fileChanged() {
      this.files = this.fileInput.files ? this.fileInput.files : null;
    },
  },
  computed: {
    fileInput(): HTMLInputElement {
      return this.$refs.upload as HTMLInputElement;
    },
  },
});
</script>

<template>
  <div class="mt-2">
    <input
      ref="upload"
      class="upload-input block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
      type="file"
      :accept="acceptFiles.join(',')"
      @change="fileChanged"
      multiple
    />
    <div class="mb-2 mt-4 flex flex-col md:flex-row justify-end items-center">
      <div v-if="loading" role="status" class="mb-4 md:mb-0 md:mr-4">
        <svg
          aria-hidden="true"
          class="w-8 h-8 md:w-8 md:h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
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
      <button
        @click="upload()"
        :disabled="!files || files.length == 0"
        class="upload-songs-button mx-auto md:mx-0 cursor-pointer w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        <slot></slot>
      </button>
    </div>
    <span v-if="fileError" class="text-red-600 dark:text-red-400">{{ fileError }}</span>
  </div>
</template>

<style></style>
