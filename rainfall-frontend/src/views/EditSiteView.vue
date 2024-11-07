<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { type Site } from '../types/site';
import DeployButton from '../components/DeployButton.vue';
import PreviewSiteButton from '../components/PreviewSiteButton.vue';
import DeleteConfirmModal from '../components/DeleteConfirmModal.vue';
import Release from '../components/Release.vue';
import { getCsrf } from '../helpers/cookie';
import { deleteSite as deleteSiteHelper } from '@/helpers/site';

export default {
  components: { DeployButton, PreviewSiteButton, Release, DeleteConfirmModal },
  data(): {
    site: null | Site;
    newSiteName: string;
    releaseName: string;
    newReleaseName: string;
    sitesError: string;
    renameError: string;
    createReleaseError: string;
    invalidateHandler: () => void;
    siteExists: boolean;
    deleteError: string;
  } {
    return {
      site: null,
      newSiteName: '',
      newReleaseName: '',
      releaseName: '',
      sitesError: '',
      renameError: '',
      createReleaseError: '',
      invalidateHandler: () => {},
      siteExists: false,
      deleteError: '',
    };
  },
  async created() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (!user) {
      this.$router.replace('/');
      return;
    }
    if (!user.is_welcomed) {
      this.$router.replace('/welcome');
    }
    this.$watch(
      () => this.$route.params,
      (toParams, previousParams) => {
        if (toParams.site_id !== previousParams.site_id) {
          this.loadSite();
        }
      },
    );
    await this.loadSite();
    await this.calculateSiteExists();
  },
  computed: {
    readyForPreview() {
      return (
        this.site &&
        this.site.releases.length > 0 &&
        this.site.releases.some((release) => {
          return release.files.length > 0;
        })
      );
    },
    ...mapStores(useUserStore),
  },
  methods: {
    async loadSite() {
      this.invalidateHandler();
      const resp = await fetch(`/api/v1/site/${this.$route.params.site_id}`);
      if (resp.ok) {
        this.site = await resp.json();
        this.newSiteName = this.site ? this.site.name : '';
        return;
      }

      let error = 'An unknown error occurred';
      if (resp.headers.get('Content-Type') == 'application/json') {
        const data = await resp.json();
        error = data.error;
      }
      this.sitesError = error;
    },
    async deleteSite(id: string) {
      if (!this.site) {
        return;
      }
      this.deleteError = await deleteSiteHelper(this.site.id);
      this.$router.replace('/sites');
    },
    setInvalidateHandler(fn: () => void) {
      this.invalidateHandler = fn;
    },
    async createRelease() {
      if (!this.site) {
        return;
      }
      this.createReleaseError = '';
      const resp = await fetch('/api/v1/release', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({
          release: {
            name: this.newReleaseName,
            site_id: this.site.id,
          },
        }),
      });
      if (!resp.ok) {
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.createReleaseError = data.error;
        } else {
          this.createReleaseError = 'An unknown error occurred';
        }
        return;
      }
      this.loadSite();
    },
    async calculateSiteExists() {
      if (!this.site) {
        return false;
      }
      const resp = await fetch(`/api/v1/preview/${this.site.id}`);
      this.siteExists = resp.ok;
    },
    async updateName() {
      if (!this.site) {
        return;
      }
      const resp = await fetch(`/api/v1/site/${this.site.id}/name`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify({ name: this.newSiteName }),
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
      this.site.name = this.newSiteName;
    },
    showDeleteModal() {
      (this.$refs.deleteModal as typeof DeleteConfirmModal).show();
    },
  },
};
</script>

<template>
  <div>
    <div v-if="sitesError" class="max-w-screen-md">
      <p class="mt-4 text-red-600 dark:text-red-400">Could not load that site: {{ sitesError }}</p>
    </div>
    <div v-else-if="site" class="max-w-screen-md flex flex-col md:text-left">
      <h2 class="text-2xl font-bold text-left">Editing {{ site.name }}</h2>
      <p class="mt-4">
        A site is composed of Releases. Each Release represents an album, EP, single, etc. A Release
        contains a number of songs/files that you upload here. The name of the release, as well as
        the artist(s) for the site, are taken from the ID3 metadata of the files you upload.
      </p>
      <p class="mt-4">
        You can upload songs in any of the following formats: .aiff, .aif, .flac, .mp3, .ogg, .opus,
        .wav
      </p>
      <p class="mt-4">
        <strong>Max upload size is 100 MB.</strong> If you are attempting to upload files larger
        than this, try encoding to
        <a class="text-blue-400 hover:underline" href="https://en.wikipedia.org/wiki/FLAC">FLAC</a>
        or
        <a
          class="text-blue-400 hover:underline"
          href="https://en.wikipedia.org/wiki/Opus_(audio_format)"
          >Opus</a
        >. Faircamp will transcode all tracks to Opus anyways.
      </p>
      <p class="mt-4">Add a release and some files, and then you can preview your site.</p>

      <div class="max-w-screen-md md:flex md:justify-end mt-4 md:mt-0">
        <div class="flex flex-col md:flex-row w-full md:w-4/5 mt-4 justify-end items-center">
          <input
            id="site-name"
            v-model="newSiteName"
            class="w-10/12 md:w-80 mr-4 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          /><button
            id="edit-name-button"
            @click="updateName"
            :disabled="!newSiteName || newSiteName === site.name"
            class="cursor-pointer mt-4 md:mt-0 p-4 md:py-2 w-10/12 md:w-48 md:h-10 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-gray-200 disabled:text-gray-600 disabled:text-white disabled:bg-blue-400 hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white font-bold border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
          >
            Update name
          </button>
        </div>
      </div>
      <div
        v-if="renameError"
        class="text-center md:text-right m-auto md:mr-0 w-80 md:w-auto text-red-600 dark:text-red-400 mt-4"
      >
        {{ renameError }}
      </div>

      <hr class="mt-12 md:hidden" />

      <div class="mt-4 flex flex-col md:flex-row items-center">
        <label
          for="new-release"
          class="block w-56 text-sm font-medium text-gray-900 dark:text-white"
          >Release name</label
        >
        <input
          id="new-release"
          v-model="newReleaseName"
          type="text"
          class="mr-4 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="New Release Name"
          maxlength="255"
          required
        />

        <div>
          <div class="flex flex-col items-center mt-4 md:mt-0 text-center">
            <button
              id="new-release-button"
              :disabled="!newReleaseName"
              @click="createRelease"
              class="cursor-pointer w-10/12 md:w-48 py-4 md:py-2 px-4 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-gray-200 disabled:text-gray-600 disabled:text-white disabled:bg-blue-400 hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white font-bold py-2 px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
            >
              Add Release
            </button>
          </div>
        </div>
      </div>
      <p
        v-if="createReleaseError"
        class="text-sm mt-2 w-10/12 md:w-1/2 text-red-600 dark:text-red-400"
      >
        {{ createReleaseError }}
      </p>

      <div class="text-left">
        <PreviewSiteButton
          :site-id="site.id"
          :ready-for-preview="readyForPreview"
          @invalidatePreview="setInvalidateHandler"
          @preview-requested="calculateSiteExists"
        />
        <DeployButton :site-id="site.id" :ready-for-deploy="readyForPreview && siteExists" />
      </div>

      <div
        v-if="site.releases.length > 0"
        class="md:max-w-screen-md mt-8 py-4 border border-emerald-500 bg-green-200 dark:bg-transparent"
      >
        <div v-for="release in site.releases" class="mb-6 last:mb-0">
          <Release
            :release="release"
            @song-uploaded="loadSite()"
            @release-deleted="loadSite()"
          ></Release>
        </div>
      </div>

      <DeleteConfirmModal
        ref="deleteModal"
        @confirm-delete="deleteSite(site.id)"
        displayMessage="Are you sure you want to delete this Site, all of its Releases, and all associated songs?"
      ></DeleteConfirmModal>
      <div class="flex flex-col md:flex-row mt-8 justify-right">
        <button
          @click="showDeleteModal()"
          id="delete-release-button"
          class="block md:w-40 md:ml-auto md:mr-4 cursor-pointer w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base bg-red-700 dark:bg-red-500 text-gray-100 font-semibold rounded hover:text-white hover:bg-red-800"
        >
          Delete Entire Site
        </button>
      </div>
    </div>
    <div v-else class="max-w-screen-md">Loading...</div>
  </div>
</template>

<style></style>
