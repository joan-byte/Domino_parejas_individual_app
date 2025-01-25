<template>
  <div class="asignacion-mesas">
    <div class="header">
      <h2>Asignación de Mesas</h2>
      <div class="partida-info">
        <span>Partida: {{ partidaActual }}</span>
      </div>
    </div>
    
    <div v-if="jugadoresPaginados.length > 0">
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Mesa</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="jugador in jugadoresPaginados" :key="jugador.id">
            <td>{{ jugador.id }}</td>
            <td>{{ jugador.nombre }}</td>
            <td>{{ jugador.apellidos }}</td>
            <td>{{ jugador.club }}</td>
            <td>{{ jugador.mesa }}</td>
          </tr>
        </tbody>
      </table>
      <div class="paginacion-info">
        Página {{ paginaActual + 1 }} de {{ totalPaginas }}
      </div>
    </div>
    <div v-else>
      <p>No hay jugadores asignados todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(1)
let intervaloAutomatico = null

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
  }
}

// Procesar los jugadores y sus mesas asignadas
const jugadoresOrdenados = computed(() => {
  if (!parejas.value || !Array.isArray(parejas.value)) {
    return []
  }

  const jugadores = []
  parejas.value.forEach(pareja => {
    if (pareja.jugador1 && pareja.jugador2) {
      // Añadir jugador 1
      jugadores.push({
        id: pareja.jugador1_id,
        nombre: pareja.jugador1.nombre || '',
        apellidos: pareja.jugador1.apellidos || '',
        club: pareja.jugador1.club || '',
        mesa: pareja.mesa
      })
      // Añadir jugador 2
      jugadores.push({
        id: pareja.jugador2_id,
        nombre: pareja.jugador2.nombre || '',
        apellidos: pareja.jugador2.apellidos || '',
        club: pareja.jugador2.club || '',
        mesa: pareja.mesa
      })
    }
  })
  // Ordenar por ID de jugador ascendente
  return jugadores.sort((a, b) => a.id - b.id)
})

const totalPaginas = computed(() => {
  return Math.ceil(jugadoresOrdenados.value.length / jugadoresPorPagina)
})

const jugadoresPaginados = computed(() => {
  const inicio = paginaActual.value * jugadoresPorPagina
  const fin = inicio + jugadoresPorPagina
  return jugadoresOrdenados.value.slice(inicio, fin)
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

const cargarParejas = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (response.ok) {
      const data = await response.json()
      parejas.value = data
      // Iniciar paginación automática después de cargar los datos
      if (jugadoresOrdenados.value.length > jugadoresPorPagina) {
        iniciarPaginacionAutomatica()
      }
    } else {
      console.error('Error al cargar las parejas:', response.statusText)
      parejas.value = []
    }
  } catch (error) {
    console.error('Error al cargar las parejas:', error)
    parejas.value = []
  }
}

// Reiniciar el intervalo cuando cambie el número total de jugadores
watch(() => jugadoresOrdenados.value.length, (newValue) => {
  if (newValue > jugadoresPorPagina) {
    iniciarPaginacionAutomatica()
  }
})

onMounted(() => {
  checkCampeonatoSeleccionado()
  cargarParejas()
})

onUnmounted(() => {
  // Limpiar el intervalo cuando el componente se desmonte
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
})
</script>

<style scoped>
.asignacion-mesas {
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

.jugadores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  margin-bottom: 20px;
}

.jugadores-table th,
.jugadores-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.jugadores-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #2c3e50;
}

.jugadores-table tr:hover {
  background-color: #f8f9fa;
}

.paginacion-info {
  text-align: center;
  margin-top: 10px;
  font-size: 1.1em;
  color: #666;
}
</style> 