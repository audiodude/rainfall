<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';

export default {
  computed: {
    ...mapStores(useUserStore),
  },
  async mounted() {
    await this.userStore.loadUser();
  },
};
</script>

<template>
  <div class="mx-auto">
    <div>
      <span v-if="userStore.isLoggedIn" class="flex justify-center"
        ><img
          class="w-8 h-7 w-7 mr-4"
          :src="userStore.user!.picture_url"
          referrerpolicy="no-referrer"
        />
        {{ userStore.user!.email }}</span
      >
      <span v-else>Not signed in</span>
    </div>
  </div>
</template>

<style scoped></style>
