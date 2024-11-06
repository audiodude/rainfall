<script lang="ts">
import ReleaseComponent from '@/components/Release.vue';
import DeleteReleaseModal from '@/components/DeleteConfirmModal.vue';

import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import type { Release } from '@/types/release';

export default {
  components: { ReleaseComponent, DeleteReleaseModal },
  data(): { release: Release | null; releaseError: string; deleteError: string } {
    return {
      release: null,
      releaseError: '',
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
        if (toParams.release_id !== previousParams.release_id) {
          this.loadRelease();
        }
      },
    );
    await this.loadRelease();
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    async loadRelease() {
      const resp = await fetch(`/api/v1/release/${this.$route.params.release_id}`);
      if (resp.ok) {
        this.release = await resp.json();
        return;
      }

      let error = 'An unknown error occurred';
      if (resp.headers.get('Content-Type') == 'application/json') {
        const data = await resp.json();
        error = data.error;
      }
      this.releaseError = error;
    },
  },
};
</script>

<template>
  <div>
    <div v-if="releaseError">
      <p class="mt-4 text-red-600 dark:text-red-400">
        Could not load that release: {{ releaseError }}
      </p>
    </div>
    <div v-if="release">
      <div class="text-3xl">Editing {{ release.name }}</div>
      <div class="mt-4">
        <a :href="`/site/${release.site_id}`">
          <svg
            id="left-arrow"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-6 h-6 inline"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"
            />
          </svg>
          Back to site
        </a>
      </div>
      <ReleaseComponent
        :release="release"
        @song-uploaded="loadRelease()"
        :isEditing="true"
      ></ReleaseComponent>
    </div>
  </div>
</template>
