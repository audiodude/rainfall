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
  methods: {
    async signOut() {
      await this.userStore.signOut();
      this.$router.replace('/');
    },
  },
};
</script>

<template>
  <div v-if="userStore.isLoggedIn">
    <button
      @click="signOut()"
      class="sign-out bg-transparent hover:bg-blue-500 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded"
    >
      Sign out
    </button>
  </div>
</template>

<style scoped></style>
