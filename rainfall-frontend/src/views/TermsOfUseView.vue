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
    <div name="termly-embed" data-id="8d548f55-b957-4759-a0aa-807d9934d6c1"></div>
  </div>
</template>
