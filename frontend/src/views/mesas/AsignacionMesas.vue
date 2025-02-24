<template>
  <div class="asignacion-mesas">
    <div class="header no-print">
      <h2>Asignación de Mesas</h2>
      <div class="header-actions">
        <div class="partida-info">
          <span>Partida: {{ partidaActual }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="jugadoresPaginados.length > 0" class="no-print">
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Mesa</th>
            <th>Pareja</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="jugador in jugadoresPaginados" :key="jugador.id">
            <td>{{ jugador.id }}</td>
            <td>{{ jugador.nombre }}</td>
            <td>{{ jugador.apellidos }}</td>
            <td>{{ jugador.club }}</td>
            <td>{{ jugador.mesa }}</td>
            <td>{{ jugador.numero_pareja }}</td>
          </tr>
        </tbody>
      </table>
      <div class="paginacion-info">
        Página {{ paginaActual + 1 }} de {{ totalPaginas }}
      </div>
    </div>

    <ImpresionMesas 
      :mesas-por-pagina="mesasPorPagina"
      :partida-actual="partidaActual"
    />

    <div v-if="jugadoresPaginados.length === 0" class="no-print">
      <p>No hay jugadores asignados todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ImpresionMesas from '@/components/ImpresionMesas.vue'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(0)
let intervaloAutomatico = null

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 0
  }
}

// Procesar los jugadores y sus mesas asignadas
const jugadoresOrdenados = computed(() => {
  if (!parejas.value || !Array.isArray(parejas.value)) {
    return []
  }

  // Usar un Map para asegurarnos de que cada jugador aparezca solo una vez
  const jugadoresMap = new Map()

  parejas.value.forEach(pareja => {
    // Procesar jugador1 siempre que exista
    if (pareja.jugador1) {
      jugadoresMap.set(pareja.jugador1_id, {
        id: pareja.jugador1_id,
        nombre: pareja.jugador1.nombre || '',
        apellidos: pareja.jugador1.apellidos || '',
        club: pareja.jugador1.club || '',
        mesa: pareja.mesa,
        numero_pareja: pareja.numero_pareja
      })
    }
    
    // Procesar jugador2 siempre que exista
    if (pareja.jugador2) {
      jugadoresMap.set(pareja.jugador2_id, {
        id: pareja.jugador2_id,
        nombre: pareja.jugador2.nombre || '',
        apellidos: pareja.jugador2.apellidos || '',
        club: pareja.jugador2.club || '',
        mesa: pareja.mesa,
        numero_pareja: pareja.numero_pareja
      })
    }
  })

  // Convertir el Map a array y ordenar por ID
  return Array.from(jugadoresMap.values()).sort((a, b) => a.id - b.id)
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
    checkCampeonatoSeleccionado()
    if (!campeonatoSeleccionado.value) {
      console.error('No hay campeonato seleccionado')
      return
    }

    // Primero, obtener la última partida con registros
    const ultimaPartidaResponse = await fetch(`http://localhost:8000/api/parejas-partida/ultima-partida/${campeonatoId}`)
    if (!ultimaPartidaResponse.ok) {
      console.error('Error al obtener la última partida')
      return
    }
    const { ultima_partida, tiene_registros } = await ultimaPartidaResponse.json()
    
    // Si no hay registros, establecer partida_actual a 0
    if (!tiene_registros) {
      partidaActual.value = 0
      parejas.value = []
      // Actualizar el localStorage
      if (campeonatoSeleccionado.value) {
        campeonatoSeleccionado.value.partida_actual = 0
        localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonatoSeleccionado.value))
      }
      return
    }

    // Actualizar la partida actual con la última partida válida
    partidaActual.value = ultima_partida
    console.log('Cargando parejas para partida:', partidaActual.value)
    
    // Actualizar el localStorage con la partida actual correcta
    if (campeonatoSeleccionado.value) {
      campeonatoSeleccionado.value.partida_actual = partidaActual.value
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonatoSeleccionado.value))
    }
    
    // Obtener las parejas de la partida actual
    const parejasResponse = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (!parejasResponse.ok) {
      console.error('Error al cargar las parejas:', parejasResponse.statusText)
      parejas.value = []
      return
    }
    const parejasData = await parejasResponse.json()
    console.log('Parejas cargadas:', parejasData)

    // Asignar los puntos iniciales a cada jugador
    parejas.value = parejasData.map(pareja => ({
      ...pareja,
      jugador1: {
        ...pareja.jugador1,
        PG: pareja.jugador1?.PP || 150,
        PC: pareja.jugador1?.PC || 0
      },
      jugador2: pareja.jugador2 ? {
        ...pareja.jugador2,
        PG: pareja.jugador2?.PP || 150,
        PC: pareja.jugador2?.PC || 0
      } : null
    }))

    if (jugadoresOrdenados.value.length > jugadoresPorPagina) {
      iniciarPaginacionAutomatica()
    }
  } catch (error) {
    console.error('Error al cargar los datos:', error)
    parejas.value = []
  }
}

// Agregar un watcher para el campeonatoSeleccionado
watch(() => campeonatoSeleccionado.value?.partida_actual, async (newPartida, oldPartida) => {
  if (newPartida !== oldPartida) {
    console.log('Partida actual cambió:', newPartida)
    await cargarParejas()
  }
})

onMounted(() => {
  checkCampeonatoSeleccionado()
  if (campeonatoSeleccionado.value) {
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 0
  }
  cargarParejas()
  
  // Agregar listener para cambios en el localStorage
  window.addEventListener('storage', () => {
    console.log('Storage changed, reloading data...')
    checkCampeonatoSeleccionado()
    cargarParejas()
  })

  // Agregar listener para evento personalizado de actualización
  window.addEventListener('update-asignacion-mesas', () => {
    console.log('Received update-asignacion-mesas event')
    cargarParejas()
  })
})

onUnmounted(() => {
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  window.removeEventListener('storage', () => {
    checkCampeonatoSeleccionado()
    cargarParejas()
  })
  window.removeEventListener('update-asignacion-mesas', () => {
    cargarParejas()
  })
})

// Computed para tener un array plano de mesas
const mesasAplanadas = computed(() => {
  const mesasMap = new Map()
  
  parejas.value.forEach(pareja => {
    if (!mesasMap.has(pareja.mesa)) {
      mesasMap.set(pareja.mesa, {
        numero: parseInt(pareja.mesa),
        pareja1: null,
        pareja2: null
      })
    }
    
    const mesaActual = mesasMap.get(pareja.mesa)
    if (pareja.numero_pareja === 1) {
      mesaActual.pareja1 = pareja
    } else if (pareja.numero_pareja === 2) {
      mesaActual.pareja2 = pareja
    }
  })

  // Convertir el Map a array y mantener todas las mesas, incluso las incompletas
  return Array.from(mesasMap.values())
    .sort((a, b) => parseInt(a.numero) - parseInt(b.numero))
})

// Computed para tener las mesas organizadas por páginas
const mesasPorPagina = computed(() => {
  const paginas = []
  for (let i = 0; i < mesasAplanadas.value.length; i += 2) {
    const pagina = {
      mesa1: mesasAplanadas.value[i],
      mesa2: i + 1 < mesasAplanadas.value.length ? mesasAplanadas.value[i + 1] : null
    }
    paginas.push(pagina)
  }
  return paginas
})
</script>

<style scoped>
/* Mantener solo los estilos para la vista normal, eliminar los estilos de impresión */
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
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

.print-only {
  display: none;
}

@media print {
  .no-print {
    display: none !important;
  }
}
</style> 