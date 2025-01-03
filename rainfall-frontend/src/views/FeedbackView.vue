<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '@/stores/user';
import Feedback from '@/components/Feedback.vue';

export default {
  components: { Feedback },
  async mounted() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (!user) {
      this.$router.replace('/');
      return;
    }
    if (!user.is_welcomed) {
      this.$router.replace('/welcome');
    }
  },
  computed: {
    ...mapStores(useUserStore),
  },
};
</script>

<template>
  <Feedback></Feedback>
</template>
