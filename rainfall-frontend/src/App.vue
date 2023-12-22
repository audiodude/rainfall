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
    <div class="w-full mx-auto max-w-screen-xl p-4 md:flex md:items-center md:justify-between">
      <a
        href="https://www.flaticon.com/free-icons/rain"
        title="rain icons"
        class="text-sm text-gray-900 dark:text-white"
        >Rain icons created by tulpahn - Flaticon</a
      >
      <span class="block md:inline"
        >Questions? Bugs?
        <a class="text-blue-500 hover:underline" href="https://github.com/audiodude/rainfall/issues"
          >File a Github issue</a
        ></span
      >
    </div>
  </footer>
</template>

<style scoped></style>
