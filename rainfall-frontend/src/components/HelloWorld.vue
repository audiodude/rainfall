<script lang="ts">
export default {
  data() {
    return {
      name: 'Beta',
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      redirectUri: import.meta.env.VITE_GOOGLE_REDIRECT_URI,
    };
  },
};
</script>

<template>
  <h1>Rainfall {{ name }}</h1>
  <div
    id="g_id_onload"
    :data-client_id="clientId"
    data-ux_mode="redirect"
    :data-login_uri="redirectUri"
  ></div>
  <div class="g_id_signin" data-type="standard"></div>
</template>

<style scoped></style>
