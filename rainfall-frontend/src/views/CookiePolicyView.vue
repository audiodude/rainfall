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
    <div name="termly-embed" data-id="e074f095-ba3f-476e-a964-ec4e4df892fd"></div>
  </div>
</template>
