<script lang="ts">
import SignIn from '../components/SignIn.vue';
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';

export default {
  async mounted() {
    await this.userStore.loadUser();
  },
  computed: {
    ...mapStores(useUserStore),
  },
};
</script>

<template>
  <main>
    <SignIn />
  </main>
</template>
