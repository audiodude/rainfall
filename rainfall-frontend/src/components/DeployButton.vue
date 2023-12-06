<script lang="ts">
import { initFlowbite } from 'flowbite';
import { routeLocationKey } from 'vue-router';
export default {
  props: ['siteId', 'readyForDeploy'],
  data(): {} {
    return {};
  },
  computed: {
    downloadUrl() {
      return `/api/v1/zip/${this.siteId}`;
    },
  },
  mounted() {
    initFlowbite();
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md md:text-left">
      <!-- focus:ring-4 focus:outline-none focus:ring-blue-300 inline-flex items-center -->
      <button
        id="dropdownDefaultButton"
        :disabled="!readyForDeploy"
        data-dropdown-toggle="dropdown"
        class="mt-4 w-10/12 md:w-32 text-xl md:text-base py-4 md:py-2 px-4 focus:ring-4 text-gray-200 disabled:text-gray-600 focus:outline-none focus:ring-blue-300 inline-flex items-center justify-center cursor-pointer disabled:cursor-auto bg-blue-600 disabled:bg-blue-400 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white font-bold border border-blue-500 rounded hover:text-white hover:border-transparent disabled:hover:border-blue-600"
        type="button"
      >
        Deploy
        <svg
          class="w-2.5 h-2.5 ms-3 relative top-0.5"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 10 6"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="m1 1 4 4 4-4"
          />
        </svg>
      </button>

      <!-- Dropdown menu -->
      <div
        id="dropdown"
        class="z-10 hidden bg-white divide-y divide-gray-100 rounded-lg shadow w-44 dark:bg-gray-700"
      >
        <ul
          class="py-2 text-sm text-gray-700 dark:text-gray-200"
          aria-labelledby="dropdownDefaultButton"
        >
          <li>
            <a
              :href="downloadUrl"
              class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
              >Download .ZIP</a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style></style>
