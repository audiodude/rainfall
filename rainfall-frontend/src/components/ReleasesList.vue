<script lang="ts">
import SongUpload from './SongUpload.vue';

export default {
  components: { SongUpload },
  props: ['releases'],
  methods: {
    uploadSong() {},
  },
};
</script>

<template>
  <div>
    <div v-if="releases.length > 0" class="md:max-w-screen-md mt-8 p-4 border border-emerald-500">
      <div v-for="release in releases" class="mb-6 last:mb-0">
        <div class="flex flex-row justify-between p-2 bg-emerald-500 text-white">
          <span class="release-name">
            {{ release.name }}
          </span>
        </div>
        <div v-for="file of release.files" class="text-right my-2">
          {{ file.filename }}
        </div>
        <div v-if="release.files.length == 0" class="text-right mt-4">
          <span class="italic">No files uploaded yet</span>
        </div>
        <hr class="my-4" />
        <div class="text-right">
          <SongUpload :releaseId="release.id" class="md:ml-40" />
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
