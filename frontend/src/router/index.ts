import { createRouter, createWebHistory } from 'vue-router'
import CrearCampeonato from '../views/CrearCampeonato.vue'
import ModificarCampeonato from '../views/ModificarCampeonato.vue'
import Home from '../views/Home.vue'
import Inscripcion from '../views/Inscripcion.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/crear-campeonato',
    name: 'crear-campeonato',
    component: CrearCampeonato
  },
  {
    path: '/modificar-campeonato/:id',
    name: 'modificar-campeonato',
    component: ModificarCampeonato
  },
  {
    path: '/inscripcion/:campeonatoId',
    name: 'inscripcion',
    component: Inscripcion
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 