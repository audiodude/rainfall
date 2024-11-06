<script lang="ts">
import DeleteConfirmModal from './DeleteConfirmModal.vue';

import { deleteSite as deleteSiteHelper } from '@/helpers/site';

export default {
  components: { DeleteConfirmModal },
  props: ['sites'],
  data() {
    return {
      deleteError: '',
      siteIdToDelete: null,
    };
  },
  methods: {
    editSite(id: string) {
      this.$router.push(`/site/${id}`);
    },
    async deleteSite() {
      this.deleteError = await deleteSiteHelper(this.siteIdToDelete);
      this.siteIdToDelete = null;
      this.$emit('site-deleted');
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
          <button
            @click="
              siteIdToDelete = site.id;
              $refs.deleteModal?.show();
            "
            type="button"
            class="delete-site-overview-button"
          >
            <svg
              class="inline text-red-700 dark:text-red-600 w-6 h-6 relative -top-0.5 ml-px"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
            </svg>
          </button>
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
    <DeleteConfirmModal
      ref="deleteModal"
      @confirm-delete="deleteSite()"
      displayMessage="Are you sure you want to delete this Site, all of its Releases, and all associated songs?"
    ></DeleteConfirmModal>
  </div>
</template>

<style></style>
