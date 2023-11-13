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
      <div v-for="release in releases" class="mb-2 last:mb-0">
        <div class="flex flex-row justify-between p-2 bg-emerald-500 text-white">
          <span class="release-name">
            {{ release.name }}
          </span>
        </div>
        <div class="text-right">
          <SongUpload :releaseId="release.id" class="ml-10" />
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
