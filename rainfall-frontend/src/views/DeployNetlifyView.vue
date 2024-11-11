<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '@/stores/user';
import { getCsrf } from '@/helpers/cookie';
import { type Site } from '@/types/site';

export default {
  data(): {
    site: null | Site;
    sitesError: string;
    siteExists: boolean;
    deployError: string;
    deploying: boolean;
    forceHideDeployWarning: boolean;
  } {
    return {
      site: null,
      sitesError: '',
      siteExists: false,
      deployError: '',
      deploying: false,
    };
  },
  async created() {
    await this.loadSite();
  },
  async mounted() {
    await this.userStore.loadUser();
    await this.calculateSiteExists();
    const user = this.userStore.user;
    if (!user) {
      this.$router.replace('/');
      return;
    }
    if (!user.is_welcomed) {
      this.$router.replace('/welcome');
    }
    if (!this.siteExists) {
      this.$router.replace(`/site/${this.$route.params.site_id}`);
    }
  },
  computed: {
    hasNetlifyToken(): boolean {
      return !!this.userStore.user?.integration?.netlify_access_token;
    },
    ...mapStores(useUserStore),
  },
  methods: {
    getCsrf() {
      return getCsrf();
    },
    async calculateSiteExists() {
      const resp = await fetch(`/api/v1/preview/${this.$route.params.site_id}`);
      this.siteExists = resp.ok;
    },
    async loadSite() {
      const resp = await fetch(`/api/v1/site/${this.$route.params.site_id}`);
      if (resp.ok) {
        this.site = await resp.json();
        return;
      }

      let error = 'An unknown error occurred';
      if (resp.headers.get('Content-Type') == 'application/json') {
        const data = await resp.json();
        error = data.error;
      }
      this.sitesError = error;
    },
    async deploySite() {
      if (!this.hasNetlifyToken || !this.site) {
        return;
      }

      this.deployError = '';
      this.deploying = true;
      this.forceHideDeployWarning = true;
      const resp = await fetch(`/api/v1/oauth/netlify/${this.site.id}/deploy`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      });
      this.deploying = false;

      if (!resp.ok) {
        this.deployError = 'An unknown error occurred';
        if (resp.headers.get('Content-Type') == 'application/json') {
          const data = await resp.json();
          this.deployError = data.error;
        }
      }

      await this.loadSite();
    },
  },
};
</script>

<template>
  <div>
    <div class="max-w-screen-md">
      <h2 class="text-gray-900 dark:text-white text-2xl md:text-2xl font-extrabold mb-2">
        Host site on Netlify
      </h2>
      <p class="mt-4">
        <a class="text-blue-500 hover:underline" href="https://www.netlify.com/">Netlify</a> will
        host your artist site for free. You can use this page to automatically deploy your site
        there, without having to download the ZIP file and upload it yourself. You must first
        <a class="text-blue-500 hover:underline" href="https://app.netlify.com/signup">sign up</a>
        for a free Netlify account, or log in if you already have one.
      </p>
      <p class="mt-4">
        When you click the "Connect to Netlify" button below, you will be brought to the Netlify
        website and asked to connect your Netlify account to Rainfall. After that, you will return
        to this page to deploy the site.
      </p>
      <form
        class="flex flex-col items-center md:items-start"
        action="/api/v1/oauth/netlify/login"
        method="POST"
      >
        <div
          v-if="sitesError || deployError"
          id="error-list"
          class="mt-2 mb-2 text-sm text-red-600 dark:text-red-400"
        >
          <div>{{ sitesError }}</div>
          <div>{{ deployError }}</div>
        </div>
        <button
          id="netlify-connect-button"
          class="cursor-pointer mx-auto md:mx-0 mt-4 w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
        >
          Connect to Netlify
        </button>
        <p v-if="hasNetlifyToken" class="mt-1 italic text-sm text-center md:text-left">
          You have already connected your Netlify account.
        </p>

        <input type="hidden" name="site_id" :value="site?.id" />
        <input type="hidden" name="_csrf_token" :value="getCsrf()" />
      </form>
      <p v-if="hasNetlifyToken" class="mt-4 text-orange-600 dark:text-orange-400">
        Clicking the "Deploy" button will make your site live on the web. Additional clicks will
        cause your site to be replaced with your current preview.
      </p>
      <div class="mt-4 flex flex-col md:flex-row md:justify-start">
        <button
          id="netlify-deploy-button"
          @click="deploySite()"
          :disabled="!hasNetlifyToken"
          class="cursor-pointer mx-auto md:mx-0 w-10/12 md:w-48 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
        >
          Deploy
        </button>
        <div v-if="deploying" role="status" class="my-2 m-auto md:ml-4">
          <svg
            aria-hidden="true"
            class="loader w-12 h-12 md:w-8 md:h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
            viewBox="0 0 100 101"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
              fill="currentColor"
            />
            <path
              d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
              fill="currentFill"
            />
          </svg>
          <span class="sr-only">Deploying your site...</span>
        </div>
        <div
          v-if="site && site.netlify_url && !deploying"
          class="ml-4 mt-1 md:mt-0 text-sm text-center md:text-left md:leading-[2.5rem]"
        >
          <a :href="site.netlify_url" target="_blank" class="text-blue-500 hover:underline"
            >Your site is live at:<br class="md:hidden" />
            {{ site.netlify_url }}</a
          >
        </div>
      </div>
    </div>
  </div>
</template>
