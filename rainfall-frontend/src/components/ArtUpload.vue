<script lang="ts">
import { defineComponent } from 'vue';
import UploadButton from './UploadButton.vue';

export default defineComponent({
  props: {
    releaseId: { type: String, required: true },
  },
  components: { UploadButton },
  data() {
    return {
      nonce: this.generateNonce(),
    };
  },
  computed: {
    artworkUrl() {
      return `/api/v1/release/${this.releaseId}/artwork?nonce=${this.nonce}`;
    },
    imageBackgroundStyle() {
      return { backgroundImage: `url('${this.artworkUrl}')` };
    },
  },
  methods: {
    generateNonce() {
      let nonce = '';
      for (let i = 0; i < 8; i++) {
        nonce += Math.floor(Math.random() * 10);
      }
      return nonce;
    },
    reloadImage() {
      this.nonce = this.generateNonce();
    },
  },
});
</script>

<template>
  <div>
    <div
      class="bg-gray-500 w-[50%] p-[50%] md:w-[25%] md:p-[25%] bg-contain"
      :style="imageBackgroundStyle"
    ></div>
    <UploadButton
      :upload-url="`/api/v1/upload/release/${releaseId}/art`"
      param-name="artwork"
      :accept-files="['.gif', '.jpg', '.jpeg', '.png', '.webp']"
      class="md:mr-[50%]"
      @song-uploaded="reloadImage()"
      >Upload art</UploadButton
    >
  </div>
</template>
