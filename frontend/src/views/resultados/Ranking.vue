<template>
  <div class="ranking-container">
    <div class="header">
      <h2>Ranking</h2>
      <div class="partida-info">
        <span>Partida: {{ partidaActual }}</span>
      </div>
    </div>
    
    <table v-if="jugadoresPaginados.length > 0" class="ranking-table">
      <thead>
        <tr>
          <th>Ranking</th>
          <th>Partida</th>
          <th>PG</th>
          <th>PC</th>
          <th>PT</th>
          <th>ID</th>
          <th>Nombre</th>
          <th>Apellidos</th>
          <th>Club</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(jugador, index) in jugadoresPaginados" :key="jugador.id">
          <td>{{ paginaActual * jugadoresPorPagina + index + 1 }}</td>
          <td :class="{ 'partida-pendiente': jugador.ultima_partida < partidaActual }">
            {{ jugador.ultima_partida }}
          </td>
          <td>{{ jugador.PG }}</td>
          <td>{{ jugador.PC }}</td>
          <td>{{ jugador.PT }}</td>
          <td>{{ jugador.jugador_id }}</td>
          <td>{{ jugador.nombre }}</td>
          <td>{{ jugador.apellidos }}</td>
          <td>{{ jugador.club }}</td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="jugadoresPaginados.length > 0" class="paginacion-info">
      Página {{ paginaActual + 1 }} de {{ totalPaginas }}
    </div>
    
    <div v-else class="no-data">
      No hay datos de ranking disponibles.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const parejas = ref([])
const resultados = ref([])
const partidaActual = ref(1)
const campeonatoSeleccionado = ref(null)
const rankingData = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
let intervaloAutomatico = null

const totalPaginas = computed(() => {
  return Math.ceil(rankingData.value.length / jugadoresPorPagina)
})

const jugadoresPaginados = computed(() => {
  const inicio = paginaActual.value * jugadoresPorPagina
  const fin = inicio + jugadoresPorPagina
  return rankingData.value.slice(inicio, fin)
})

const siguientePagina = () => {
  if (paginaActual.value < totalPaginas.value - 1) {
    paginaActual.value++
  } else {
    paginaActual.value = 0 // Volver al inicio
  }
}

const iniciarPaginacionAutomatica = () => {
  // Limpiar intervalo existente si hay uno
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  
  // Crear nuevo intervalo
  intervaloAutomatico = setInterval(() => {
    siguientePagina()
  }, 10000) // 10 segundos
}

// Reiniciar el intervalo cuando cambie el número total de jugadores
watch(() => rankingData.value.length, (newValue) => {
  if (newValue > jugadoresPorPagina) {
    iniciarPaginacionAutomatica()
  }
})

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
  }
}

const cargarDatos = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoSeleccionado.value.id}`)
    if (response.ok) {
      const data = await response.json()
      rankingData.value = data
    } else {
      console.error('Error al cargar el ranking:', response.statusText)
      rankingData.value = []
    }
  } catch (error) {
    console.error('Error al cargar el ranking:', error)
    rankingData.value = []
  }
}

onMounted(() => {
  checkCampeonatoSeleccionado()
  window.addEventListener('storage', checkCampeonatoSeleccionado)
  window.addEventListener('ranking-update', cargarDatos)
  
  // Cargar datos iniciales
  cargarDatos()
})

onUnmounted(() => {
  window.removeEventListener('storage', checkCampeonatoSeleccionado)
  window.removeEventListener('ranking-update', cargarDatos)
  // Limpiar el intervalo cuando el componente se desmonte
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
})
</script>

<style scoped>
.ranking-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ranking-table th,
.ranking-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.ranking-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #2c3e50;
}

.ranking-table tr:hover {
  background-color: #f8f9fa;
}

.paginacion-info {
  text-align: center;
  margin-top: 10px;
  font-size: 1.1em;
  color: #666;
}

.no-data {
  text-align: center;
  color: #666;
  margin: 20px 0;
  font-size: 1.1em;
}

.partida-pendiente {
  color: #dc3545;
  font-weight: bold;
}
</style> 