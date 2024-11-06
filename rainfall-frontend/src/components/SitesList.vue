<script lang="ts">
import DeleteConfirmModal from './DeleteConfirmModal.vue';

import { deleteSite as deleteSiteHelper } from '@/helpers/site';

export default {
  components: { DeleteConfirmModal },
  props: ['sites'],
  data(): {
    deleteError: string;
    siteIdToDelete: string | null;
  } {
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
      if (!this.siteIdToDelete) {
        return;
      }
      this.deleteError = await deleteSiteHelper(this.siteIdToDelete);
      this.siteIdToDelete = null;
      this.$emit('site-deleted');
    },
    showDeleteModal(id: string) {
      this.siteIdToDelete = id;
      (this.$refs.deleteModal as typeof DeleteConfirmModal).show();
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
        <span
          @click="editSite(site.id)"
          class="site-name w-full flex justify-between cursor-pointer"
        >
          {{ site.name }}
          <button
            @click.stop="showDeleteModal(site.id)"
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
