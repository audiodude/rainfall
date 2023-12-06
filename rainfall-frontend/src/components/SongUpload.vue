<script lang="ts">
export default {
  props: ['releaseId'],
  data(): { files: FileList | null; fileError: string | null } {
    return {
      files: null,
      fileError: null,
    };
  },
  methods: {
    async upload() {
      if (!this.files) {
        return;
      }

      this.fileError = null;

      let formData = new FormData();
      for (const song of this.files) {
        formData.append('song[]', song);
      }
      formData.append('release_id', this.releaseId);
      const resp = await fetch('/api/v1/upload', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });
      if (resp.ok) {
        this.files = null;
        this.fileInput.value = '';
        this.$emit('song-uploaded');
        return;
      }

      let error = 'An unknown error occurred';
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
};
</script>

<template>
  <div class="mt-2">
    <input
      ref="upload"
      class="upload-input block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
      type="file"
      accept=".aiff,.aif,.flac,.mp3,.ogg,.opus,.wav"
      @change="fileChanged"
      multiple
    />
    <label class="block mb-2" for="multiple_files">
      <button
        @click="upload()"
        :disabled="!files || files.length == 0"
        class="upload-songs-button cursor-pointer mt-4 py-4 md:py-2 px-4 disabled:cursor-auto bg-blue-500 focus:ring-4 focus:outline-none focus:ring-blue-300 disabled:bg-blue-400 hover:bg-blue-700 disabled:hover:bg-blue-400 font-semibold text-gray-200 disabled:text-gray-600 font-bold py-2 px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
      >
        Upload Songs
      </button></label
    >
    <span v-if="fileError" class="text-red-600 dark:text-red-400">{{ fileError }}</span>
  </div>
</template>

<style></style>
