<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import NavBar from './components/NavBar.vue';
</script>

<template>
  <header class="max-h-15">
    <NavBar />
  </header>

  <RouterView class="container max-w-screen-xl mx-auto grow shrink-0 p-4" />

  <footer class="border-gray-200 shadow bg-gray-800 shrink">
    <div
      class="w-full mx-auto max-w-screen-xl p-4 md:flex md:items-center md:justify-between text-gray-300"
    >
      <div>
        <span class="block md:inline"
          >Questions? Bugs?
          <a
            class="text-blue-500 hover:underline"
            href="https://github.com/audiodude/rainfall/issues"
            >File a Github issue.</a
          ></span
        >
        <span class="block md:inline">
          We welcome
          <a
            class="text-blue-500 hover:underline"
            href="https://docs.google.com/forms/d/e/1FAIpQLSca4myLs9S0kw1DTA5MOB2OGUDP27f6qaTBELT2oDXjAEyUHw/viewform?usp=header"
            >feedback</a
          >
        </span>
      </div>
      <div>
        <span class="block md:inline mr-4">
          <a class="text-blue-500 hover:underline" href="/terms">Terms of Use</a>
        </span>
        <span class="block md:inline mr-4">
          <a class="text-blue-500 hover:underline" href="/privacy-policy">Privacy Policy</a>
        </span>

        <span class="block md:inline">
          <a class="text-blue-500 hover:underline" href="/cookie-policy">Cookie Policy</a>
        </span>
      </div>
    </div>
    <div></div>
  </footer>
</template>

<style scoped></style>
