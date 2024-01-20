<script lang="ts">
// import SignIn from '../components/SignIn.vue';
import { mapStores } from 'pinia';
import { useUserStore } from '../stores/user';
import SignIn from '../components/SignIn.vue';

export default {
  async mounted() {
    await this.userStore.loadUser();
  },
  computed: {
    ...mapStores(useUserStore),
  },
  components: { SignIn },
};
</script>

<template>
  <main>
    <section>
      <div class="py-8 px-4 mx-auto max-w-screen-xl lg:pt-16 lg:pb-8">
        <div
          class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12 mb-8"
        >
          <a
            href="#"
            class="bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-blue-400 mb-2"
          >
            <svg
              class="w-2.5 h-2.5 me-1.5"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 14"
            >
              <path
                d="M11 0H2a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2Zm8.585 1.189a.994.994 0 0 0-.9-.138l-2.965.983a1 1 0 0 0-.685.949v8a1 1 0 0 0 .675.946l2.965 1.02a1.013 1.013 0 0 0 1.032-.242A1 1 0 0 0 20 12V2a1 1 0 0 0-.415-.811Z"
              />
            </svg>
            Rainfall
          </a>
          <h1 class="text-gray-900 dark:text-white text-3xl md:text-5xl font-extrabold mb-2">
            Your music. Your website. Your way.
          </h1>
          <p class="text-lg font-normal text-gray-500 dark:text-gray-400 mb-6">
            <em>Rainfall</em> let's you create a website for your music, using
            <a href="https://simonrepp.com/faircamp/" class="text-blue-500 hover:underline"
              >Faircamp</a
            >. We don't host your site or charge you anything. Upload your songs and preview your
            site, and when you're done you'll get a ZIP file that you can host anywhere on the web.
          </p>
        </div>
        <div class="grid md:grid-cols-2 gap-8">
          <div
            class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12"
          >
            <span
              class="bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-green-400 mb-2"
            >
              <svg
                class="w-2.5 h-2.5 me-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 18 18"
              >
                <path
                  d="M17 11h-2.722L8 17.278a5.512 5.512 0 0 1-.9.722H17a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1ZM6 0H1a1 1 0 0 0-1 1v13.5a3.5 3.5 0 1 0 7 0V1a1 1 0 0 0-1-1ZM3.5 15.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2ZM16.132 4.9 12.6 1.368a1 1 0 0 0-1.414 0L9 3.55v9.9l7.132-7.132a1 1 0 0 0 0-1.418Z"
                />
              </svg>
              Upload
            </span>
            <h2 class="text-gray-900 dark:text-white text-3xl font-extrabold mb-2">
              Upload your music on the web
            </h2>
            <p class="text-lg font-normal text-gray-500 dark:text-gray-400 mb-4">
              Sign into <em>Rainfall</em> with your Mastodon or Google account and start uploading
              music. You can upload in .aiff, .aif, .flac, .mp3, .ogg, .opus, or .wav.
            </p>
          </div>
          <div
            class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12"
          >
            <span
              class="bg-purple-100 text-purple-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-purple-400 mb-2"
            >
              <svg
                class="w-2.5 h-2.5 me-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 20 16"
              >
                <path
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 4 1 8l4 4m10-8 4 4-4 4M11 1 9 15"
                />
              </svg>
              Download
            </span>
            <h2 class="text-gray-900 dark:text-white text-3xl font-extrabold mb-2">
              Preview and Download your site
            </h2>
            <p class="text-lg font-normal text-gray-500 dark:text-gray-400 mb-4">
              We will generate a preview link that is for your eyes only. When you're ready, you can
              download a ZIP file of your finished site.
            </p>
          </div>
        </div>
      </div>
    </section>

    <SignIn class="px-4 mx-auto max-w-auto pr-10" />
  </main>
</template>
