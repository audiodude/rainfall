<script lang="ts">
import { defineComponent } from 'vue';
import UploadButton from './UploadButton.vue';

export default defineComponent({
  props: {
    releaseId: { type: String, required: true },
  },
  components: { UploadButton },
});
</script>

<template>
  <div>
    <div class="bg-gray-500 w-[50%] p-[50%] md:w-[25%] md:p-[25%]"></div>
    <UploadButton
      :uploadUrl="`/api/v1/upload/release/${releaseId}`"
      releaseId=""
      class="md:mr-[50%]"
      >Upload art</UploadButton
    >
  </div>
</template>
