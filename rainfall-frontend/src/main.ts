import './assets/main.css';
import 'flowbite';

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';
// @ts-ignore
import VueMatomo from 'vue-matomo';

import './index.css';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(VueMatomo, {
  host: 'https://rainfalldev.matomo.cloud/',
  siteId: 1,
});

app.mount('#app');

(window as unknown as any)._paq.push(['trackPageView']);
