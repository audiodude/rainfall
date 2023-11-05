<script lang="ts">
// import SignIn from '../components/SignIn.vue';
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import SignIn from '../components/SignIn.vue';

export default {
  async mounted() {
    await this.userStore.loadUser();
  },
  computed: {
    ...mapStores(useUserStore),
  },
  components: { SignIn },
};
</script>

<template>
  <main>
    <h1 class="text-4xl mt-4">Not Found</h1>
    <p class="mt-4">Sorry, we couldn't find anything at that URL.</p>
    <p class="mt-4">
      <a
        href="/"
        class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
        >Go home</a
      >
    </p>
  </main>
</template>
