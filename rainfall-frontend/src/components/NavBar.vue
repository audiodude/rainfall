<script lang="ts">
import UserState from './UserState.vue';
import SignOutButton from './SignOutButton.vue';

export default {
  components: { UserState, SignOutButton },
};
</script>

<template>
  <nav class="border-gray-200 bg-gray-800">
    <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
      <RouterLink to="/" class="flex items-center">
        <img src="@/assets/rain.png" class="h-8 mr-3" alt="Rainfall Logo" />
        <span class="self-center text-2xl font-semibold whitespace-nowrap text-white"
          >Rainfall</span
        >
      </RouterLink>
      <ul
        class="w-full md:w-auto font-medium flex flex-col text-center md:text-left p-4 md:p-0 mt-4 border rounded-lg md:flex-row md:space-x-8 md:mt-0 md:border-0 bg-gray-800 border-gray-700"
      >
        <li>
          <RouterLink
            to="/sites"
            class="block py-2 pl-3 pr-4 text-gray-900 rounded h-8 hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:pt-2 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:hover:bg-transparent"
            >Sites</RouterLink
          >
        </li>
        <li>
          <UserState class="user-state py-2 pl-3 pr-4 md:pt-2 text-white" />
        </li>
        <li>
          <SignOutButton class="py-2 pl-3 pr-4 md:p-0 text-white" />
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped></style>
