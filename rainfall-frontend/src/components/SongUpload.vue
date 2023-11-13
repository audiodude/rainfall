<script lang="ts">
export default {
  props: ['releaseId'],
  data(): { files: FileList | null } {
    return {
      files: null,
    };
  },
  methods: {
    upload() {
      if (!this.files) {
        return;
      }
      let formData = new FormData();
      for (const song of this.files) {
        formData.append('song[]', song);
      }
      formData.append('release_id', this.releaseId);
      fetch('/api/v1/upload', { method: 'POST', credentials: 'include', body: formData });
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
      class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
      type="file"
      accept=".aiff,.aif,.flac,.mp3,.ogg,.opus,.wav"
      @change="fileChanged"
      multiple
    />
    <label class="block mb-2" for="multiple_files">
      <button
        id="new-release-button"
        @click="upload()"
        :disabled="!files || files.length == 0"
        class="cursor-pointer mt-1 disabled:cursor-auto bg-transparent hover:bg-blue-500 disabled:hover:bg-transparent font-semibold hover:text-white disabled:hover:dark:text-gray-300 py-2 px-4 border border-blue-500 hover:border-transparent disabled:hover:border-blue-500 rounded"
      >
        Upload Songs
      </button></label
    >
  </div>
</template>

<style></style>
