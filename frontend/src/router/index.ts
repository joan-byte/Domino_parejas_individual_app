import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CrearCampeonato from '../views/CrearCampeonato.vue'
import ModificarCampeonato from '../views/ModificarCampeonato.vue'
import Inscripcion from '../views/Inscripcion.vue'
import AsignacionMesas from '../views/mesas/AsignacionMesas.vue'
import RegistroMesas from '../views/mesas/RegistroMesas.vue'
import ImprimirMesas from '../views/mesas/ImprimirMesas.vue'
import Ranking from '../views/resultados/Ranking.vue'
import Podium from '../views/resultados/Podium.vue'
import ImprimirRanking from '../views/resultados/ImprimirRanking.vue'

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
    path: '/mesas/imprimir/:campeonatoId',
    name: 'imprimir-mesas',
    component: ImprimirMesas
  },
  {
    path: '/resultados/ranking/:campeonatoId',
    name: 'ranking',
    component: Ranking
  },
  {
    path: '/resultados/podium/:campeonatoId',
    name: 'podium',
    component: Podium
  },
  {
    path: '/resultados/ranking/imprimir/:campeonatoId',
    name: 'imprimir-ranking',
    component: ImprimirRanking
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 