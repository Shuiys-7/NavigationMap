import { createRouter, createWebHistory } from 'vue-router'
import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'
import HomeLayout from '../components/HomeLayout.vue'
import BIDashboard from '../components/BIDashboard.vue'
import MapPage from '../components/MapPage.vue'
import NavigationMapPage from '../components/NavigationMapPage.vue'
import ProfilePage from '../components/ProfilePage.vue'
import DataPage from '../components/DataPage.vue'
import EditPage from '../components/EditPage.vue'
import VisitPage from '../components/VisitPage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginForm },
  { path: '/register', component: RegisterForm },
  {
    path: '/home',
    component: HomeLayout,
    children: [
      { path: '', redirect: 'dashboard' },
      { path: 'dashboard', component: BIDashboard },
      { path: 'showcase', component: MapPage },
      { path: 'navigation', component: NavigationMapPage },
      { path: 'data', component: DataPage },
      { path: 'edit', component: EditPage },
      { path: 'profile', component: ProfilePage },
      { path: 'visit', component: VisitPage }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
