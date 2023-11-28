<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { type Site } from '../types/site';
import ReleaseActions from '../components/ReleaseActions.vue';
import ReleasesList from '../components/ReleasesList.vue';

export default {
  components: { ReleaseActions, ReleasesList },
  data(): { site: null | Site; sitesError: string; invalidateHandler: () => void } {
    return {
      site: null,
      sitesError: '',
      invalidateHandler: () => {},
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
  },
};
</script>

<template>
  <div>
    <div v-if="sitesError" class="max-w-screen-md">
      <p class="mt-4 text-red-600 dark:text-red-400">Could not load that site: {{ sitesError }}</p>
    </div>
    <div v-else-if="site" class="max-w-screen-md">
      <h2 class="text-2xl font-bold">Editing {{ site.name }}</h2>
      <p class="mt-4">
        A site is composed of Releases. Each Release represents an album, EP, single, etc. A Release
        contains a number of songs/files that you upload here. The name of the release, as well as
        the artist(s) for the site, are taken from the ID3 metadata of the files you upload.
      </p>
      <p class="mt-4">
        You can upload songs in any of the following formats: .aiff, .aif, .flac, .mp3, .ogg, .opus,
        .wav
      </p>
      <p class="mt-4">Add a release and some files, and then you can preview your site.</p>
      <ReleaseActions
        :cardinality="cardinality"
        :site-id="site.id"
        :ready-for-preview="readyForPreview"
        @release-created="loadSite"
        @invalidatePreview="setInvalidateHandler"
      />
      <ReleasesList :releases="site.releases" @song-uploaded="loadSite()" />
    </div>
    <div v-else class="max-w-screen-md">Loading...</div>
  </div>
</template>

<style></style>