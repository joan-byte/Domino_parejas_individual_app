import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Inscripcion from '../views/Inscripcion.vue'
import AsignacionMesas from '../views/mesas/AsignacionMesas.vue'
import RegistroMesas from '../views/mesas/RegistroMesas.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/inscripcion/:campeonatoId',
      name: 'inscripcion',
      component: Inscripcion
    },
    {
      path: '/mesas/asignacion/:campeonatoId',
      name: 'asignacion-mesas',
      component: AsignacionMesas
    },
    {
      path: '/mesas/registro/:campeonatoId',
      name: 'registro-mesas',
      component: RegistroMesas
    }
  ]
})

export default router 