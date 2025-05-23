<script lang="ts">
import { defineComponent, type PropType } from 'vue';

import ArtUpload from './ArtUpload.vue';
import UploadButton from './UploadButton.vue';
import { type Release } from '../types/release';
import { getCsrf } from '../helpers/cookie';
import DeleteConfirmModal from './DeleteConfirmModal.vue';

export default defineComponent({
  props: {
    release: { type: Object as PropType<Release | null>, required: true },
    isEditing: Boolean,
  },
  components: { ArtUpload, UploadButton, DeleteConfirmModal },
  data() {
    return {
      newReleaseName: '',
      currentDescription: '',
      descriptionError: '',
      renameError: '',
      deleteError: '',
      deleteSongError: '',
      stashedDescription: '',
    };
  },
  created() {
    if (!this.release) {
      return;
    }
    this.currentDescription = this.release.description;
    this.newReleaseName = this.release.name;
  },
  methods: {
    onSongUploaded() {
      if (this.release) {
        this.stashedDescription = this.release.description;
      }
      this.$emit('song-uploaded');
    },
    editRelease(id: string) {
      this.$router.push(`/release/${id}`);
    },
    async updateDescription() {
      if (!this.release) {
        return;
      }
      const resp = await fetch(`/api/v1/release/${this.release.id}/description`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify({ description: this.release.description }),
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.descriptionError = data.error;
        }
        return;
      }
      this.currentDescription = this.release.description;
    },
    async updateName() {
      if (!this.release) {
        return;
      }
      const resp = await fetch(`/api/v1/release/${this.release.id}/name`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify({ name: this.newReleaseName }),
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.renameError = data.error;
        } else {
          this.renameError = 'An unknown error occurred';
        }
        return;
      }
      this.release.name = this.newReleaseName;
    },
    async deleteFile(release: Release, id: string) {
      const resp = await fetch(`/api/v1/file/${id}`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrf() },
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.deleteSongError = data.error;
        } else {
          this.deleteSongError = 'An unknown error occurred';
        }
        return;
      }
      const i = release.files.findIndex((file) => file.id == id);
      release.files.splice(i, 1);
    },
    async deleteRelease(id: string) {
      const resp = await fetch(`/api/v1/release/${id}`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrf() },
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.deleteError = data.error;
        } else {
          this.deleteError = 'An unknown error occurred';
        }
        return;
      }
      this.$emit('release-deleted');
      if (this.release && this.isEditing) {
        this.$router.push(`/site/${this.release.site_id}`);
      }
    },
    showDeleteModal() {
      (this.$refs.deleteModal as typeof DeleteConfirmModal).show();
    },
  },
  watch: {
    release(newRelease) {
      newRelease.description = this.stashedDescription;
    },
  },
});
</script>

<template>
  <div v-if="release">
    <div
      :class="
        isEditing
          ? 'md:max-w-screen-md mt-8 p-4 border border-emerald-500 bg-green-200 dark:bg-transparent'
          : ''
      "
      class="release"
    >
      <div v-if="isEditing" class="max-w-screen-md md:flex md:justify-end my-2 md:mt-0">
        <div class="flex flex-col md:flex-row w-full md:w-4/5 mb-2 justify-end items-center">
          <input
            id="site-name"
            v-model="newReleaseName"
            class="max-w-xl bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          /><button
            id="edit-name-button"
            @click="updateName"
            :disabled="!newReleaseName || newReleaseName === release.name"
            class="cursor-pointer mt-4 md:mt-0 p-4 md:py-2 w-10/12 md:w-48 md:h-10 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-gray-200 disabled:text-gray-600 disabled:text-white disabled:bg-blue-400 hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white font-bold border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
          >
            Update name
          </button>
        </div>
      </div>
      <div
        v-if="renameError"
        class="text-center md:text-right m-auto md:mr-0 w-80 md:w-auto text-red-600 dark:text-red-400 mb-4"
      >
        {{ renameError }}
      </div>

      <div v-if="isEditing" class="flex flex-row flex-wrap justify-between">
        <div class="art-upload-cont w-full md:w-[48%]">
          <ArtUpload :releaseId="release.id"></ArtUpload>
        </div>
        <div class="desc-edit-cont w-full md:w-[48%]">
          <textarea
            id="release-description"
            v-model="release.description"
            placeholder="Enter a description about your release"
            class="w-full h-[24.75rem] text-black"
          ></textarea>
          <button
            id="update-description-button"
            :disabled="release.description === '' || release.description === currentDescription"
            @click="updateDescription()"
            class="block md:w-40 mx-auto md:ml-auto md:mr-0 cursor-pointer mt-4 w-10/12 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
          >
            Update
          </button>
          <span v-if="descriptionError" class="text-red-600 dark:text-red-400">{{
            descriptionError
          }}</span>
        </div>
      </div>

      <div v-if="!isEditing" class="p-2 bg-emerald-500 text-white">
        <div class="release-name text-xl flex justify-between">
          {{ release.name }}
          <button @click="showDeleteModal()" type="button" class="delete-release-overview-button">
            <svg
              class="inline text-red-600 w-6 h-6 relative -top-0.5 ml-px"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
            </svg>
          </button>
        </div>
        <a
          class="text-gray-800 hover:text-gray-500 hover:underline cursor-pointer"
          @click.prevent="editRelease(release.id)"
          >edit art/description</a
        >
      </div>
      <div :class="{ 'mx-4': !isEditing }">
        <div v-if="isEditing" class="text-emerald-700 dark:text-emerald-500 text-xl">
          Songs
          <hr class="h-px my-2 border-emerald-500" />
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
        <div
          v-if="deleteSongError"
          class="delete-song-error-msg mt-2 text-red-600 dark:text-red-400"
        >
          <div>
            {{ deleteSongError }}
          </div>
        </div>
        <div
          v-if="deleteError && !isEditing"
          class="delete-error-msg-top mt-2 text-red-600 dark:text-red-400"
        >
          <div>
            {{ deleteError }}
          </div>
        </div>
        <div v-if="release.files.length == 0" class="text-right mt-4">
          <span class="no-files-msg italic">No files uploaded</span>
        </div>
        <hr v-if="!isEditing" class="my-4 border-emerald-500" />
        <div class="text-right">
          <UploadButton
            :upload-url="`/api/v1/upload/release/${release.id}/song`"
            param-name="song[]"
            :accept-files="['.aiff', '.alac', '.aif', '.flac', '.mp3', '.ogg', '.opus', '.wav']"
            @song-uploaded="onSongUploaded()"
            class="md:ml-40"
          >
            Upload songs
          </UploadButton>
        </div>
      </div>
    </div>
    <DeleteConfirmModal
      ref="deleteModal"
      @confirm-delete="deleteRelease(release.id)"
      displayMessage="Are you sure you want to delete this Release and all associated songs?"
    ></DeleteConfirmModal>
    <div v-if="isEditing" class="md:max-w-screen-md pr-4">
      <button
        @click="showDeleteModal()"
        id="delete-release-button"
        class="block md:w-40 mx-auto md:ml-auto md:mr-0 cursor-pointer mt-4 w-10/12 p-4 md:py-2 text-xl md:text-base bg-red-700 dark:bg-red-500 text-gray-100 font-semibold rounded hover:text-white hover:bg-red-600"
      >
        Delete release
      </button>
      <div
        v-if="deleteError"
        class="delete-error-msg text-center md:text-right m-auto md:mr-0 w-80 md:w-auto text-red-600 dark:text-red-400 mb-4"
      >
        {{ deleteError }}
      </div>
    </div>
  </div>
</template>

<style></style>
