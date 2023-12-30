<script lang="ts">
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import { getCsrf } from '../helpers/cookie';

export default {
  data() {
    return {
      ready: false,
    };
  },
  async mounted() {
    await this.userStore.loadUser();
    const user = this.userStore.user;
    if (!user) {
      this.$router.replace('/');
      return;
    }
    if (user.is_welcomed) {
      this.$router.replace('/sites');
    }
  },
  computed: {
    ...mapStores(useUserStore),
  },
  methods: {
    async getStarted() {
      const resp = await fetch('/api/v1/user/welcome', {
        method: 'POST',
        headers: { 'X-CSRFToken': await getCsrf() },
      });
      if (resp.ok) {
        await this.userStore.loadUser(/* force */ true);
        this.$router.push('/sites');
      }
    },
  },
};
</script>

<template>
  <div>
    <div class="md:max-w-screen-md pl-4 mt-4">
      <h1 class="text-3xl mt-4">Welcome!</h1>
      <p class="mt-4">
        <em>Rainfall</em> is an app that let's you create a website for your music. If you're an
        artist, whether professional or amateur, you can use Rainfall to generate the source code
        for your music's home on the web. You can host the generated site on your own, using any
        number of website hosts:
      </p>
      <ul class="list-disc ml-8 mt-4 space-y-4">
        <li>
          <a
            href="https://www.netlify.com/"
            class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
            >Netlify</a
          >
        </li>
        <li>
          <a
            href="https://cloud.google.com/storage?hl=en"
            class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
            >Google Cloud</a
          >
        </li>
        <li>
          <a
            href="https://aws.amazon.com/s3/"
            class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
            >Amazon Web Services</a
          >
        </li>
        <li>
          <a
            href="https://render.com"
            class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
            >Render</a
          >
        </li>
        <li>
          <a
            href="https://pages.cloudflare.com/"
            class="text-blue-600 dark:text-blue-300 visited:text-teal-600 dark:visited:text-teal-300 hover:underline"
            >Cloudflare Pages</a
          >
        </li>
        <li>And many others!</li>
      </ul>
      <p class="mt-4">
        Using the Rainfall tools, you will upload your songs, and add any necessary metadata. Next,
        you will preview your site. Finally, when it's time to publish, you can choose to integrate
        with Netlify and publish your site automatically, or even download a .ZIP file of your
        website to take wherever you like.
      </p>
      <p class="mt-4">
        Keep in mind: Rainfall will <em>not</em> be hosting your site! Rainfall only exists to help
        you gather your materials and metadata and generate your music website.
      </p>
      <div class="flex flex-row mt-8">
        <div class="flex flex-col justify-center">
          <input v-model="ready" name="agree" type="checkbox" class="block max-w-sm" />
        </div>
        <div class="ml-4 max-w-2xl">
          <label for="agree" class="text-lg">
            I understand that Rainfall will not make my songs or site available to the outside
            world, and I will have complete ownership for where and how they get published
            (including any liability for copyright issues).</label
          >
        </div>
      </div>
      <div class="mt-8 max-w-xs mx-auto md:mx-0 text-center md:text-left">
        <button
          @click="getStarted()"
          :disabled="!ready"
          class="get-started cursor-pointer mt-4 w-10/12 md:w-32 p-4 md:py-2 text-xl md:text-base disabled:cursor-auto bg-blue-600 text-grey-200 disabled:bg-blue-400 disabled:text-white hover:bg-blue-800 disabled:hover:bg-blue-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-semibold text-gray-100 hover:text-white px-4 border border-blue-500 rounded hover:border-transparent disabled:hover:border-blue-500"
        >
          Get started!
        </button>
      </div>
    </div>
  </div>
</template>

<style></style>
