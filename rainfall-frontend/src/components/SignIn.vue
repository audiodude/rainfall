<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';

export default {
  data() {
    return {
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      redirectUri: import.meta.env.VITE_GOOGLE_REDIRECT_URI,
    };
  },
  computed: {
    ...mapStores(useUserStore),
  },
  async mounted() {
    await this.userStore.loadUser();
    if (!this.userStore.isLoggedIn) {
      let googleScript = document.createElement('script');
      googleScript.setAttribute('src', 'https://accounts.google.com/gsi/client');
      document.head.appendChild(googleScript);
    }
  },
};
</script>

<template>
  <div v-if="!userStore.isLoggedIn">
    <h1>Sign in:</h1>
    <div
      id="g_id_onload"
      :data-client_id="clientId"
      data-ux_mode="redirect"
      :data-login_uri="redirectUri"
    ></div>
    <div class="g_id_signin" data-type="standard"></div>
  </div>
</template>

<style scoped>
.g_id_signin {
  max-width: 12rem;
}
</style>
