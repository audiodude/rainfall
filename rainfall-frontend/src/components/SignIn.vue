<script lang="ts">
import { mapState, mapStores } from 'pinia';
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
    ...mapState(useUserStore, ['isLoggedIn']),
  },
  async mounted() {
    await this.userStore.loadUser();
    if (!this.isLoggedIn) {
      this.mountGoogleScript();
    }
  },
  methods: {
    mountGoogleScript() {
      let googleScript = document.createElement('script');
      googleScript.setAttribute('src', 'https://accounts.google.com/gsi/client');
      document.head.appendChild(googleScript);
    },
    signInMastodon() {
      this.$router.push('/mastodon');
    },
  },
  watch: {
    isLoggedIn(oldValue, newValue) {
      if (!oldValue && newValue) {
        this.mountGoogleScript();
      }
    },
  },
};
</script>

<template>
  <div v-if="!userStore.isLoggedIn" class="w-[19rem]">
    <div class="bg-gray-200 dark:bg-gray-800 px-4 py-2">
      <button
        type="button"
        @click="signInMastodon()"
        class="cursor-pointer flex gap-3 p-2 my-2 mx-auto bg-white w-full rounded border-solid border-black"
      >
        <div>
          <span
            class="font-medium font-roboto text-gray-900 text-xs ml-[1.85rem] mr-3 text-[#3c4043]"
            >Sign In with Mastodon</span
          >
        </div>
        <div class="flex items-center justify-center">
          <svg
            class="relative top-0.5 left-2"
            xmlns="http://www.w3.org/2000/svg"
            width="18px"
            height="18px"
            viewBox="0 0 216.4144 232.00976"
          >
            <path
              fill="#2b90d9"
              d="M211.80734 139.0875c-3.18125 16.36625-28.4925 34.2775-57.5625 37.74875-15.15875 1.80875-30.08375 3.47125-45.99875 2.74125-26.0275-1.1925-46.565-6.2125-46.565-6.2125 0 2.53375.15625 4.94625.46875 7.2025 3.38375 25.68625 25.47 27.225 46.39125 27.9425 21.11625.7225 39.91875-5.20625 39.91875-5.20625l.8675 19.09s-14.77 7.93125-41.08125 9.39c-14.50875.7975-32.52375-.365-53.50625-5.91875C9.23234 213.82 1.40609 165.31125.20859 116.09125c-.365-14.61375-.14-28.39375-.14-39.91875 0-50.33 32.97625-65.0825 32.97625-65.0825C49.67234 3.45375 78.20359.2425 107.86484 0h.72875c29.66125.2425 58.21125 3.45375 74.8375 11.09 0 0 32.975 14.7525 32.975 65.0825 0 0 .41375 37.13375-4.59875 62.915"
            />
            <path
              fill="#fff"
              d="M177.50984 80.077v60.94125h-24.14375v-59.15c0-12.46875-5.24625-18.7975-15.74-18.7975-11.6025 0-17.4175 7.5075-17.4175 22.3525v32.37625H96.20734V85.42325c0-14.845-5.81625-22.3525-17.41875-22.3525-10.49375 0-15.74 6.32875-15.74 18.7975v59.15H38.90484V80.077c0-12.455 3.17125-22.3525 9.54125-29.675 6.56875-7.3225 15.17125-11.07625 25.85-11.07625 12.355 0 21.71125 4.74875 27.8975 14.2475l6.01375 10.08125 6.015-10.08125c6.185-9.49875 15.54125-14.2475 27.8975-14.2475 10.6775 0 19.28 3.75375 25.85 11.07625 6.36875 7.3225 9.54 17.22 9.54 29.675"
            />
          </svg>
        </div>
      </button>
    </div>
    <div
      id="g_id_onload"
      :data-client_id="clientId"
      data-ux_mode="redirect"
      :data-login_uri="redirectUri"
      data-enable_redirect_uri_validation="true"
      data-auto_prompt="false"
      class="mx-auto text-center"
    ></div>
    <div class="g_id_signin" data-type="standard"></div>
  </div>
</template>

<style scoped>
.g_id_signin {
  max-width: 100%;
  background-color: #e5e7eb;
  margin: auto;
  padding: 0.6rem 1.2rem 0.8rem;
}

@media (prefers-color-scheme: dark) {
  .g_id_signin {
    background-color: #1f2937;
  }
}
</style>
