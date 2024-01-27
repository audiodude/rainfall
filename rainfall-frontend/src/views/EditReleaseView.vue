<script lang="ts">
import ReleaseComponent from '@/components/Release.vue';
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import type { Release } from '@/types/release';

export default {
  components: { ReleaseComponent },
  data(): { release: Release | null; releaseError: string } {
    return {
      release: null,
      releaseError: '',
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
    onSongUploaded() {},
  },
};
</script>

<template>
  <div>
    <div v-if="!releaseError && release" class="text-3xl">Editing {{ release.name }}</div>
    <div class="md:max-w-screen-md mt-8 p-4 border border-emerald-500">
      <ReleaseComponent
        :release="release"
        @song-uploaded="onSongUploaded()"
        :isEditing="true"
      ></ReleaseComponent>
    </div>
  </div>
</template>
