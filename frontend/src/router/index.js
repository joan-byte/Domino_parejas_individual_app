import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Inscripcion from '../views/Inscripcion.vue'
import AsignacionMesas from '../views/mesas/AsignacionMesas.vue'
import RegistroMesas from '../views/mesas/RegistroMesas.vue'
import CrearCampeonato from '../views/CrearCampeonato.vue'
import ModificarCampeonato from '../views/ModificarCampeonato.vue'
import Ranking from '../views/resultados/Ranking.vue'
import Podium from '../views/resultados/Podium.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
    },
    {
      path: '/resultados/ranking',
      name: 'ranking',
      component: Ranking
    },
    {
      path: '/resultados/podium',
      name: 'podium',
      component: Podium
    }
  ]
})

export default router 