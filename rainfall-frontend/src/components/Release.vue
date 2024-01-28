<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import ArtUpload from './ArtUpload.vue';
import UploadButton from './UploadButton.vue';
import { type Release } from '../types/release';
import { getCsrf } from '../helpers/cookie';

export default defineComponent({
  props: {
    release: { type: Object as PropType<Release | null>, required: true },
    isEditing: Boolean,
  },
  components: { ArtUpload, UploadButton },
  methods: {
    onSongUploaded() {
      this.$emit('song-uploaded');
    },
    editRelease(id: string) {
      this.$router.push(`/release/${id}`);
    },
    async deleteFile(release: Release, id: string) {
      const resp = await fetch(`/api/v1/file/${id}`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrf() },
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
});
</script>

<template>
  <div v-if="release">
    <div v-if="isEditing"><ArtUpload releaseId="release.id"></ArtUpload></div>
    <div v-if="isEditing">Description</div>
    <div v-if="!isEditing" class="p-2 bg-emerald-500 text-white">
      <div class="release-name text-xl">
        {{ release.name }}
      </div>
      <a
        class="text-gray-800 hover:text-gray-500 hover:underline"
        @click="editRelease(release.id)"
        href="#"
        >edit art/description</a
      >
    </div>
    <div v-else class="text-emerald-500 text-xl">
      Songs
      <hr class="h-px my-2 bg-emerald-500 border-0" />
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
      <UploadButton
        :uploadUrl="`/api/v1/upload/release/${release.id}/song`"
        @song-uploaded="onSongUploaded()"
        class="md:ml-40"
      >
        Upload songs
      </UploadButton>
    </div>
  </div>
</template>

<style></style>
