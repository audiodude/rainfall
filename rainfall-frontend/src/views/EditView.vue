<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';

export default {
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
      this.$router.replace('/new');
    }
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    async createSite() {
      this.createError = false;
      const resp = await fetch('/api/v1/site/create');
      if (!resp.ok) {
        setTimeout(() => {
          this.createError = true;
        }, 250);
      }
    },
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md p-4">
      <p class="mt-4">
        Rainfall uses <a href="https://simonrepp.com/faircamp/">Faircamp</a> to generate your music
        website. The advantage of using Rainfall versus using Faircamp directly is that you can
        easily upload your songs and manage your metadata. No need to install Faircamp or manage
        directory hierarchies yourself.
      </p>
      <p v-if="!site" class="mt-4">
        When you're ready, click "Create site" to start working on your website.
      </p>
      <div class="mt-4">
        <button
          @click="createSite"
          class="cursor-pointer disabled:cursor-auto bg-transparent hover:bg-blue-500 disabled:hover:bg-transparent font-semibold hover:text-white disabled:hover:dark:text-gray-300 py-2 px-4 border border-blue-500 hover:border-transparent disabled:hover:border-blue-500 rounded"
        >
          Create site
        </button>
        <p v-if="createError" class="text-sm text-red-500">
          Something went wrong while creating your site.
        </p>
      </div>
    </div>
  </div>
</template>

<style></style>
