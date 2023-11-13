<script lang="ts">
export default {
  props: ['releases'],
  methods: {
    uploadSong() {},
  },
};
</script>

<template>
  <div>
    <div v-if="releases.length > 0" class="md:max-w-screen-md mt-8 p-4 border border-emerald-500">
      <div v-for="release in releases" class="mb-2 last:mb-0">
        <div class="flex flex-row justify-between p-2 bg-emerald-500 text-white">
          <span class="release-name">
            {{ release.name }}
          </span>
        </div>
        <div class="text-right">
          <button
            id="new-release-button"
            @click="uploadSong()"
            class="ml-auto mr-0 mt-2 cursor-pointer disabled:cursor-auto bg-transparent hover:bg-emerald-500 disabled:hover:bg-transparent font-semibold hover:text-white disabled:hover:dark:text-gray-300 py-2 px-4 border border-emerald-500 hover:border-transparent disabled:hover:border-emerald-500 rounded"
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
