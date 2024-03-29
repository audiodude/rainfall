import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import WelcomeView from '../views/WelcomeView.vue';
import SitesView from '../views/SitesView.vue';
import MastodonLoginView from '../views/MastodonLoginView.vue';
import NotFoundView from '../views/NotFoundView.vue';
import EditSiteView from '../views/EditSiteView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/welcome',
      name: 'welcome',
      component: WelcomeView,
    },
    {
      path: '/sites',
      name: 'sites',
      component: SitesView,
    },
    {
      path: '/site/:site_id',
      name: 'editSite',
      component: EditSiteView,
    },
    { path: '/mastodon', name: 'mastodonLogin', component: MastodonLoginView },
    { path: '/:pathMatch(.*)*', name: 'notfound', component: NotFoundView },
  ],
});

export default router;
