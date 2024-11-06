<script lang="ts">
import { mapStores } from 'pinia';

import { useUserStore } from '@/stores/user';
import NewSite from '@/components/NewSite.vue';
import SitesList from '@/components/SitesList.vue';
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue';

export default {
  components: { NewSite, SitesList, DeleteConfirmModal },
  data() {
    return {
      sitesError: '',
      sites: [],
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
    await this.reloadSites();
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    async reloadSites() {
      const resp = await fetch('/api/v1/site/list');
      if (resp.ok) {
        const data = await resp.json();
        this.sites = data.sites;
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
    <h2 class="text-2xl font-bold">Sites</h2>
    <div v-if="sitesError" class="mt-4 text-lg text-red-500">
      Could not load your sites: {{ sitesError }}
    </div>
    <div v-else>
      <div class="md:max-w-screen-md">
        <p class="mt-4">
          Rainfall uses <a href="https://simonrepp.com/faircamp/">Faircamp</a> to generate your
          music website. The advantage of using Rainfall versus using Faircamp directly is that you
          can easily upload your songs and manage your metadata. No need to install Faircamp or
          manage directory hierarchies yourself.
        </p>
        <p v-if="sites.length == 0" class="mt-4">
          When you're ready, click "Create site" to start working on your website.
        </p>
      </div>
      <NewSite @site-created="reloadSites()" class="mt-4" />
      <SitesList :sites="sites" @site-deleted="reloadSites()" />
    </div>
  </div>
</template>

<style></style>
