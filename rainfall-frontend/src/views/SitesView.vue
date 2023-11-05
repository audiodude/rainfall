<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import NewSite from '../components/NewSite.vue';

export default {
  components: { NewSite },
  data() {
    return {
      createError: false,
      site: null,
    };
  },
  async mounted() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (!user) {
      this.$router.replace('/');
      return;
    }
    if (!user.is_welcomed) {
      this.$router.replace('/welcome');
    }
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    reloadSites() {},
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md">
      <p class="mt-4">
        Rainfall uses <a href="https://simonrepp.com/faircamp/">Faircamp</a> to generate your music
        website. The advantage of using Rainfall versus using Faircamp directly is that you can
        easily upload your songs and manage your metadata. No need to install Faircamp or manage
        directory hierarchies yourself.
      </p>
      <p v-if="!site" class="mt-4">
        When you're ready, click "Create site" to start working on your website.
      </p>
    </div>
    <NewSite @site-created="reloadSites()" class="mt-4" />
  </div>
</template>

<style></style>
