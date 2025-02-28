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

    <div v-if="jugadoresPaginados.length === 0" class="no-print">
      <p>No hay jugadores asignados todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const campeonatoId = ref(route.params.campeonatoId)
const parejas = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(0)
let intervaloAutomatico = null

// Verificar y obtener el campeonato seleccionado
const checkCampeonatoSeleccionado = () => {
  console.log('Verificando campeonato seleccionado...')
  
  // Si tenemos un ID en la ruta, usarlo primero
  if (route.params.campeonatoId) {
    campeonatoId.value = route.params.campeonatoId
    console.log('ID de campeonato desde la ruta:', campeonatoId.value)
  } else {
    console.log('No hay ID de campeonato en la ruta')
  }
  
  // Verificar si hay un campeonato en localStorage
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    try {
      const campeonatoData = JSON.parse(campeonatoGuardado)
      console.log('Campeonato encontrado en localStorage:', campeonatoData)
      
      // Si no tenemos ID en la ruta, usar el del localStorage
      if (!campeonatoId.value && campeonatoData.id) {
        campeonatoId.value = campeonatoData.id.toString()
        console.log('Usando ID de campeonato desde localStorage:', campeonatoId.value)
      }
      
      // Actualizar el campeonato seleccionado
      campeonatoSeleccionado.value = campeonatoData
      
      // Actualizar la partida actual
      if (campeonatoData.partida_actual !== undefined) {
        partidaActual.value = campeonatoData.partida_actual
        console.log('Partida actual desde localStorage:', partidaActual.value)
      }
    } catch (error) {
      console.error('Error al parsear el campeonato guardado:', error)
    }
  } else {
    console.warn('No hay campeonato guardado en localStorage')
  }
  
  // Si después de todo no tenemos un ID, intentar obtener el campeonato activo
  if (!campeonatoId.value) {
    console.log('Intentando obtener campeonato activo...')
    // Intentar obtener el último campeonato activo
    fetch('http://localhost:8000/api/campeonatos')
      .then(response => response.json())
      .then(data => {
        if (data && data.length > 0) {
          // Buscar un campeonato activo
          const campeonatoActivo = data.find(c => c.activo && !c.finalizado)
          if (campeonatoActivo) {
            console.log('Campeonato activo encontrado:', campeonatoActivo)
            campeonatoId.value = campeonatoActivo.id.toString()
            campeonatoSeleccionado.value = campeonatoActivo
            partidaActual.value = campeonatoActivo.partida_actual
            localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonatoActivo))
            cargarParejas() // Recargar los datos con el nuevo campeonato
            return true
          } else {
            // Si no hay activo, usar el primero
            console.log('No hay campeonato activo, usando el primero:', data[0])
            campeonatoId.value = data[0].id.toString()
            campeonatoSeleccionado.value = data[0]
            partidaActual.value = data[0].partida_actual
            localStorage.setItem('campeonatoSeleccionado', JSON.stringify(data[0]))
            cargarParejas() // Recargar los datos con el nuevo campeonato
            return true
          }
        } else {
          console.error('No se encontraron campeonatos')
          router.push('/campeonatos')
          return false
        }
      })
      .catch(error => {
        console.error('Error al obtener campeonatos:', error)
        router.push('/campeonatos')
        return false
      })
  } else if (!campeonatoSeleccionado.value) {
    // Si tenemos ID pero no tenemos información del campeonato, intentar obtenerla
    console.log('Tenemos ID pero no información del campeonato, intentando obtenerla...')
    obtenerInfoCampeonato()
      .then(resultado => {
        if (resultado) {
          cargarParejas() // Recargar los datos con la información actualizada
        }
        return resultado
      })
      .catch(() => {
        return false
      })
  }
  
  return !!campeonatoId.value
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

// Obtener información actualizada del campeonato
const obtenerInfoCampeonato = async () => {
  if (!campeonatoId.value) {
    console.error('No hay ID de campeonato para obtener información')
    return false
  }
  
  try {
    console.log('Obteniendo información actualizada del campeonato:', campeonatoId.value)
    const response = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId.value}`)
    
    if (!response.ok) {
      throw new Error(`Error al obtener campeonato: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('Información del campeonato obtenida:', data)
    
    // Actualizar la información del campeonato
    campeonatoSeleccionado.value = data
    partidaActual.value = data.partida_actual
    
    // Actualizar en localStorage
    localStorage.setItem('campeonatoSeleccionado', JSON.stringify(data))
    
    return true
  } catch (error) {
    console.error('Error al obtener información del campeonato:', error)
    return false
  }
}

const cargarParejas = async () => {
  try {
    // Verificar que tenemos un campeonato seleccionado
    if (!checkCampeonatoSeleccionado()) {
      return
    }
    
    // Obtener información actualizada del campeonato
    await obtenerInfoCampeonato()
    
    // Si después de todo no tenemos un ID o partida actual, salir
    if (!campeonatoId.value) {
      console.error('No hay ID de campeonato para cargar parejas')
      return
    }
    
    console.log('Cargando parejas para campeonato:', campeonatoId.value, 'partida:', partidaActual.value)
    
    // Si la partida actual es 0, no hay nada que cargar
    if (partidaActual.value === 0) {
      console.log('La partida actual es 0, no hay parejas para cargar')
      parejas.value = []
      return
    }
    
    // Obtener las parejas de la partida actual
    const parejasResponse = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId.value}/partida/${partidaActual.value}`)
    if (!parejasResponse.ok) {
      console.error('Error al cargar las parejas:', parejasResponse.statusText)
      parejas.value = []
      return
    }
    
    const parejasData = await parejasResponse.json()
    console.log('Parejas cargadas:', parejasData.length)

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
    partidaActual.value = newPartida
    await cargarParejas()
  }
})

// Agregar un watcher para el ID del campeonato
watch(() => campeonatoId.value, async (newId, oldId) => {
  if (newId !== oldId) {
    console.log('ID del campeonato cambió:', newId)
    await cargarParejas()
  }
})

onMounted(async () => {
  console.log('Componente AsignacionMesas montado')
  
  // Verificar y cargar el campeonato seleccionado
  if (checkCampeonatoSeleccionado()) {
    // Obtener información actualizada del campeonato
    await obtenerInfoCampeonato()
    // Cargar las parejas
    await cargarParejas()
  }
  
  // Agregar listener para cambios en el localStorage
  window.addEventListener('storage', async () => {
    console.log('Storage changed, reloading data...')
    if (checkCampeonatoSeleccionado()) {
      await cargarParejas()
    }
  })

  // Agregar listener para evento personalizado de actualización
  window.addEventListener('update-asignacion-mesas', async () => {
    console.log('Received update-asignacion-mesas event')
    await cargarParejas()
  })
})

onUnmounted(() => {
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  window.removeEventListener('storage', () => {})
  window.removeEventListener('update-asignacion-mesas', () => {})
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

.btn-imprimir {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-imprimir:hover {
  background-color: #45a049;
}
</style> 