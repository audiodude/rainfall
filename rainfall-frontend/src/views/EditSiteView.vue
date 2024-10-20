<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { type Site } from '../types/site';
import AddReleaseButton from '../components/AddReleaseButton.vue';
import DeployButton from '../components/DeployButton.vue';
import PreviewSiteButton from '../components/PreviewSiteButton.vue';
import Release from '../components/Release.vue';
import { getCsrf } from '../helpers/cookie';

export default {
  components: { AddReleaseButton, DeployButton, PreviewSiteButton, Release },
  data(): {
    site: null | Site;
    newSiteName: string;
    sitesError: string;
    invalidateHandler: () => void;
    siteExists: boolean;
  } {
    return {
      site: null,
      newSiteName: '',
      sitesError: '',
      invalidateHandler: () => {},
      siteExists: false,
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
    cardinality() {
      if (!this.site) {
        return 0;
      }
      if (this.site.releases.length == 0) {
        return 1;
      }
      const nums = this.site.releases.map((release) => {
        return parseInt(release.name.split(' ')[1]);
      });
      return nums.sort().slice(-1)[0] + 1;
    },
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
    setInvalidateHandler(fn: () => void) {
      this.invalidateHandler = fn;
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
          this.sitesError = data.error;
        }
        return;
      }
      this.site.name = this.newSiteName;
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
        >. Faircamp will transcode all tracks to Opus anyways, so there is no advantage to uploading
        lossless, uncompressed tracks.
      </p>
      <p class="mt-4">Add a release and some files, and then you can preview your site.</p>

      <div class="max-w-screen-md md:flex md:justify-end mt-4 md:mt-0">
        <div class="flex flex-col md:flex-row w-full md:w-4/5 mt-4 justify-end items-center">
          <input
            id="site-name"
            v-model="newSiteName"
            class="w-10/12 md:w-80 h-8 mt-2 md:mt-0 px-2 py-2 md:py-4 h-10 mr-0 md:mr-4 text-gray-600"
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

      <hr class="mt-12 md:hidden" />

      <div class="flex flex-col md:flex-row mt-8 justify-between">
        <AddReleaseButton
          :cardinality="cardinality"
          :site-id="site.id"
          @release-created="loadSite"
        />
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
        class="md:max-w-screen-md mt-8 p-4 border border-emerald-500"
      >
        <div v-for="release in site.releases" class="mb-6 last:mb-0">
          <Release :release="release" @song-uploaded="loadSite()"></Release>
        </div>
      </div>
    </div>
    <div v-else class="max-w-screen-md">Loading...</div>
  </div>
</template>

<style></style>
