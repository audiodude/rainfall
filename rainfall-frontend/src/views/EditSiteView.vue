<script lang="ts">
import { type Site } from '../types/site';

export default {
  data(): { site: null | Site; sitesError: string } {
    return {
      site: null,
      sitesError: '',
    };
  },
  async created() {
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
  methods: {
    async loadSite() {
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
  },
};
</script>

<template>
  <div>
    <div v-if="sitesError">
      <p class="mt-4 text-red-500">Could not load that site: {{ sitesError }}</p>
    </div>
    <div v-else-if="site" class="max-w-screen-md">Editing {{ site.name }}</div>
    <div v-else>Loading...</div>
  </div>
</template>

<style></style>
