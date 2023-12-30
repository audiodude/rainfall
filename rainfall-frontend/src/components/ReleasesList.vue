<script lang="ts">
import SongUpload from './SongUpload.vue';
import { type Release } from '../types/release';
import { getCsrf } from '../helpers/cookie';

export default {
  components: { SongUpload },
  props: ['releases'],
  methods: {
    onSongUploaded() {
      this.$emit('song-uploaded');
    },
    async deleteFile(release: Release, id: string) {
      const resp = await fetch(`/api/v1/file/${id}`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': await getCsrf() },
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          console.error(data.error);
        }
        return;
      }
      const i = release.files.findIndex((file) => file.id == id);
      release.files.splice(i, 1);
    },
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
        <div
          v-for="file of release.files"
          class="file-name text-right my-3 flex items-center justify-end"
        >
          <div>{{ file.filename }}</div>
          <button
            @click="deleteFile(release, file.id)"
            aria-label="delete file"
            class="inline-block ml-2 text-red-500 relative top-0.5"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-6 h-6"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </button>
        </div>
        <div v-if="release.files.length == 0" class="text-right mt-4">
          <span class="no-files-msg italic">No files uploaded</span>
        </div>
        <hr class="my-4" />
        <div class="text-right">
          <SongUpload :releaseId="release.id" @song-uploaded="onSongUploaded()" class="md:ml-40" />
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
