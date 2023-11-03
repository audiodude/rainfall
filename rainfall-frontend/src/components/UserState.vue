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
  <div>
    <span v-if="userStore.isLoggedIn">Signed in! {{ userStore.user!.email }}</span>
    <span v-else>Not signed in</span>
  </div>
</template>

<style scoped></style>
