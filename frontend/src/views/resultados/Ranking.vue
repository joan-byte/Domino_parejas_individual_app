<template>
  <div class="ranking-container">
    <div class="header">
      <h2>Ranking</h2>
      <div class="partida-info">
        <span>{{ estadoPartida }}</span>
      </div>
    </div>
    
    <table v-if="jugadoresPaginados.length > 0" class="ranking-table">
      <thead>
        <tr>
          <th>Ranking</th>
          <th>Partida</th>
          <th>PG</th>
          <th>Dif.</th>
          <th>PV</th>
          <th>PT</th>
          <th>MG</th>
          <th>ID</th>
          <th>Nombre</th>
          <th>Apellidos</th>
          <th>Club</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(jugador, index) in jugadoresPaginados" :key="jugador.id">
          <td>{{ paginaActual * jugadoresPorPagina + index + 1 }}</td>
          <td :class="{ 'partida-pendiente': !campeonatoFinalizado && jugador.ultima_partida < partidaActual }">
            {{ jugador.ultima_partida }}
          </td>
          <td>{{ jugador.PG }}</td>
          <td>{{ jugador.PC }}</td>
          <td>{{ jugador.PV }}</td>
          <td>{{ jugador.PT }}</td>
          <td>{{ jugador.MG }}</td>
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
      <p>No hay datos de ranking disponibles.</p>
      <p v-if="!campeonatoFinalizado && partidaActual > 1" class="hint">
        Los resultados se mostrarán cuando se registren las puntuaciones de la partida actual.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useEventBus } from '@vueuse/core'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = parseInt(route.params.campeonatoId)
const parejas = ref([])
const resultados = ref([])
const partidaActual = ref(1)
const partidaMostrada = ref(1)
const campeonatoSeleccionado = ref(null)
const rankingData = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
const tournamentName = ref('')
const campeonatoFinalizado = ref(false)
let intervaloAutomatico = null

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

// Obtener la partida de los query params
const getPartidaFromUrl = () => {
  const partidaParam = route.query.partida
  return partidaParam ? parseInt(partidaParam) : 1
}

const totalPaginas = computed(() => {
  return Math.ceil(rankingData.value.length / jugadoresPorPagina)
})

const jugadoresPaginados = computed(() => {
  const inicio = paginaActual.value * jugadoresPorPagina
  const fin = inicio + jugadoresPorPagina
  return rankingData.value.slice(inicio, fin)
})

const iniciarPaginacionAutomatica = () => {
  // Limpiar intervalo existente si hay uno
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  
  // Crear nuevo intervalo
  intervaloAutomatico = setInterval(async () => {
    // Primero actualizar los datos del ranking
    await cargarRanking()
    // Luego cambiar de página si hay más de una
    if (paginaActual.value < totalPaginas.value - 1) {
      paginaActual.value++
    } else {
      paginaActual.value = 0 // Volver al inicio
    }
  }, 10000) // 10 segundos
}

// Reiniciar el intervalo cuando cambie el número total de jugadores
watch(() => rankingData.value.length, () => {
  iniciarPaginacionAutomatica()
})

// Añadir un watcher para la página actual
watch(() => paginaActual.value, () => {
  // No es necesario cargar el ranking aquí ya que los datos ya están en memoria
  // y se actualizan automáticamente cada 10 segundos
})

// Añadir un watcher para los query params
watch(() => route.query.partida, (newPartida) => {
  partidaActual.value = parseInt(newPartida) || 1
  cargarRanking()
})

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
  }
}

const cargarRanking = async () => {
  try {
    // Obtener la información del campeonato
    const campeonatoResponse = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!campeonatoResponse.ok) {
      throw new Error(`Error al obtener el campeonato: ${campeonatoResponse.status}`)
    }
    const campeonato = await campeonatoResponse.json()
    tournamentName.value = campeonato.nombre
    partidaActual.value = campeonato.partida_actual
    campeonatoFinalizado.value = campeonato.finalizado

    // Si el campeonato está finalizado, usamos el número total de partidas
    const partidaParaRanking = campeonato.finalizado ? campeonato.numero_partidas : campeonato.partida_actual
    
    // Obtener el ranking usando la partida correspondiente
    const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}?partida=${partidaParaRanking}`)
    if (!rankingResponse.ok) {
      throw new Error(`Error al obtener ranking: ${rankingResponse.status}`)
    }
    const data = await rankingResponse.json()
    
    if (!Array.isArray(data)) {
      throw new Error('La respuesta del ranking no es un array')
    }
    
    rankingData.value = data
  } catch (error) {
    console.error('Error al cargar los datos:', error)
  }
}

// Escuchar el evento de actualización
rankingBus.on(() => {
  cargarRanking()
})

onMounted(async () => {
  checkCampeonatoSeleccionado()
  window.addEventListener('storage', checkCampeonatoSeleccionado)
  
  // Establecer la partida actual desde la URL
  partidaActual.value = getPartidaFromUrl()
  
  // Cargar datos iniciales
  await cargarRanking()
  
  // Iniciar la actualización automática
  iniciarPaginacionAutomatica()
})

// Modificar el watcher de la ruta para usar campeonatoId directamente
watch(
  () => route.params.campeonatoId,
  async (newId) => {
    if (newId) {
      try {
        const response = await fetch(`http://localhost:8000/api/campeonatos/${newId}`)
        if (response.ok) {
          const campeonato = await response.json()
          localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
          campeonatoSeleccionado.value = campeonato
          await cargarRanking()
        }
      } catch (error) {
        console.error('Error al cargar el campeonato:', error)
      }
    }
  }
)

onUnmounted(() => {
  window.removeEventListener('storage', checkCampeonatoSeleccionado)
  // Limpiar el intervalo cuando el componente se desmonte
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  // Limpiar el event bus
  rankingBus.off()
})

// Texto del estado de la partida
const estadoPartida = computed(() => {
  return campeonatoFinalizado.value ? 'Clasificación Final' : `Partida: ${partidaActual.value}`
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
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.hint {
  font-size: 0.9em;
  color: #4CAF50;
  margin-top: 1rem;
  font-style: italic;
}

.partida-pendiente {
  font-size: 0.9em;
  color: #dc3545;
  margin-left: 10px;
  font-style: italic;
}
</style> 