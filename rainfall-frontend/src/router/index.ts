import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import WelcomeView from '../views/WelcomeView.vue';
import SitesView from '../views/SitesView.vue';
import MastodonLoginView from '../views/MastodonLoginView.vue';
import NotFoundView from '../views/NotFoundView.vue';
import EditSiteView from '../views/EditSiteView.vue';
import EditReleaseView from '@/views/EditReleaseView.vue';
import DeployNetlifyView from '@/views/DeployNetlifyView.vue';
import FeedbackView from '@/views/FeedbackView.vue';
import TermsOfUseView from '@/views/TermsOfUseView.vue';
import CookiePolicyView from '@/views/CookiePolicyView.vue';
import PrivacyPolicyView from '@/views/PrivacyPolicyView.vue';

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
    {
      path: '/release/:release_id',
      name: 'editRelease',
      component: EditReleaseView,
    },
    { path: '/mastodon', name: 'mastodonLogin', component: MastodonLoginView },
    { path: '/deploy/:site_id/netlify', name: 'deployNetlify', component: DeployNetlifyView },

    { path: '/feedback', name: 'feedback', component: FeedbackView },
    { path: '/terms', name: 'terms', component: TermsOfUseView },
    { path: '/cookie-policy', name: 'cookie-policy', component: CookiePolicyView },
    { path: '/privacy-policy', name: 'privacy-policy', component: PrivacyPolicyView },

    // 404 page
    { path: '/:pathMatch(.*)*', name: 'notfound', component: NotFoundView },
  ],
});

export default router;
