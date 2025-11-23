import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import PathFinder from '../views/PathFinder.vue';
import Alternatives from '../views/Alternatives.vue';
import FilterDrugs from '../views/FilterDrugs.vue';
import DrugDetails from '../views/DrugDetails.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/path', name: 'path', component: PathFinder },
    { path: '/alternatives', name: 'alternatives', component: Alternatives },
    { path: '/filter', name: 'filter', component: FilterDrugs },
    { path: '/details', name: 'details', component: DrugDetails },
  ]
});

export default router;