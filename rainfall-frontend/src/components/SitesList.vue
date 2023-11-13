<script lang="ts">
export default {
  props: ['sites'],
  methods: {
    editSite(id: string) {
      this.$router.push(`/site/${id}`);
    },
  },
};
</script>

<template>
  <div>
    <div v-if="sites.length > 0" class="md:max-w-screen-md mt-8 p-4 border border-blue-500">
      <div
        v-for="site in sites"
        class="flex flex-row justify-between p-2 mb-2 last:mb-0 bg-blue-500 text-white"
      >
        <span class="site-name w-40">
          {{ site.name }}
        </span>
        <span
          class="edit-site-button w-8 hover:text-blue-800 cursor-pointer"
          @click="editSite(site.id)"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="w-6 h-6"
          >
            <path
              d="M21.731 2.269a2.625 2.625 0 00-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 000-3.712zM19.513 8.199l-3.712-3.712-8.4 8.4a5.25 5.25 0 00-1.32 2.214l-.8 2.685a.75.75 0 00.933.933l2.685-.8a5.25 5.25 0 002.214-1.32l8.4-8.4z"
            />
            <path
              d="M5.25 5.25a3 3 0 00-3 3v10.5a3 3 0 003 3h10.5a3 3 0 003-3V13.5a.75.75 0 00-1.5 0v5.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5V8.25a1.5 1.5 0 011.5-1.5h5.25a.75.75 0 000-1.5H5.25z"
            />
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>

<style></style>
