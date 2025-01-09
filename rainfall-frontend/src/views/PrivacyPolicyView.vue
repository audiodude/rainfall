<script lang="ts">
import { embedTermly } from '@/helpers/termly';

export default {
  created() {
    embedTermly();
  },
};
</script>

<template>
  <div class="bg-white">
    <div name="termly-embed" data-id="05444eee-5ac2-46c7-a32e-f628bb6b0816"></div>
  </div>
</template>
