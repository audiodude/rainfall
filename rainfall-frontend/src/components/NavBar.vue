<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import UserState from './UserState.vue';

export default {
  components: { UserState },
  computed: {
    ...mapStores(useUserStore),
  },
  async mounted() {
    await this.userStore.loadUser();
  },
};
</script>

<template>
  <nav class="bg-white border-gray-200 dark:bg-gray-800">
    <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
      <RouterLink to="/" class="flex items-center">
        <img src="@/assets/rain.png" class="h-8 mr-3" alt="Rainfall Logo" />
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white"
          >Rainfall</span
        >
      </RouterLink>
      <ul
        class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-800 dark:border-gray-700"
      >
        <li>
          <RouterLink
            to="/new"
            class="block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent"
            >New</RouterLink
          >
        </li>
        <li>
          <RouterLink
            to="/edit"
            class="block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent"
            >Edit</RouterLink
          >
        </li>
        <li>
          <UserState />
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped></style>
