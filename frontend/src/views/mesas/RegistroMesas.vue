<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventBus } from '@vueuse/core'
import ResultadoMesaPopup from '../../components/ResultadoMesaPopup.vue'

const route = useRoute()
const router = useRouter()
const eventBus = useEventBus()

const campeonatoId = ref(route.params.campeonatoId || '')
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(null)
const esUltimaPartida = ref(false)
const ventanaSecundaria = ref(null)
const vistaSecundaria = ref('mesas')
const mesas = ref([])
const mesasConParejas = ref([])
const mesasRegistradas = ref({})
const resultadoExistente = ref(null)
const showPopup = ref(false)
const mesaSeleccionada = ref(null)
const intervaloVerificacion = ref(null)

const textoCerrarPartida = computed(() => {
  return partidaActual.value === campeonatoSeleccionado.value?.numero_partidas ? 'Finalizar Campeonato' : 'Cerrar Partida'
})

const todasMesasRegistradas = computed(() => {
  if (!mesas.value?.length) return false
  return mesas.value.every(mesa => {
    return typeof mesasRegistradas.value === 'object' && 
           mesasRegistradas.value !== null && 
           mesasRegistradas.value[mesa.numeroMesa] === true
  })
})

const esMesaIncompleta = (mesa) => {
  // Verificar si falta algún jugador o está inactivo
  const jugadoresInactivos = [
    !mesa.pareja1?.jugador1?.activo,
    !mesa.pareja1?.jugador2?.activo,
    !mesa.pareja2?.jugador1?.activo,
    !mesa.pareja2?.jugador2?.activo
  ]

  // Si algún jugador está inactivo o falta (undefined/null), la mesa es incompleta
  return jugadoresInactivos.some(inactivo => inactivo === true || inactivo === undefined)
}

const cargarMesas = async () => {
  try {
    // Limpiar el estado actual
    mesas.value = []
    mesasRegistradas.value = {}
    
    // Añadir timestamp para evitar caché
    const timestamp = new Date().getTime()
    const response = await fetch(`http://localhost:8000/api/parejas-partida/mesas/${campeonatoId.value}/${partidaActual.value}?t=${timestamp}`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })

    if (!response.ok) {
      throw new Error(`Error al cargar mesas: ${response.status}`)
    }

    const data = await response.json()
    console.log('Datos de mesas recibidos:', data)

    // Asignar todas las mesas sin filtrar
    mesas.value = data

    // Verificar si hay resultados registrados
    const responseResultados = await fetch(
      `http://localhost:8000/api/resultados/campeonato/${campeonatoId.value}/partida/${partidaActual.value}?t=${timestamp}`,
      {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      }
    )

    if (responseResultados.ok) {
      const resultados = await responseResultados.json()
      console.log('Resultados cargados:', resultados)
      
      // Actualizar el objeto mesasRegistradas
      mesasRegistradas.value = {}
      resultados.forEach(r => {
        mesasRegistradas.value[r.mesa] = true
      })
    }

    console.log('Estado final - Mesas:', mesas.value)
    console.log('Estado final - Mesas registradas:', mesasRegistradas.value)
  } catch (error) {
    console.error('Error en cargarMesas:', error)
    mostrarError('Error al cargar las mesas: ' + error.message)
  }
}

const verificarMesasRegistradas = async () => {
  try {
    // Verificar que tenemos un campeonato válido
    if (!campeonatoId.value) {
      console.log('No hay campeonato seleccionado')
      return
    }

    // Verificar que el campeonato sigue existiendo
    const campeonatoResponse = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId.value}`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })

    if (!campeonatoResponse.ok) {
      console.log('El campeonato ya no existe')
      localStorage.removeItem('campeonatoSeleccionado')
      router.push('/campeonatos')
      return
    }

    const timestamp = new Date().getTime()
    const response = await fetch(
      `http://localhost:8000/api/resultados/campeonato/${campeonatoId.value}/partida/${partidaActual.value}?t=${timestamp}`,
      {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      }
    )

    if (!response.ok) {
      throw new Error(`Error al verificar mesas registradas: ${response.status}`)
    }

    const resultados = await response.json()
    
    // Asegurarnos de que mesasRegistradas.value sea siempre un objeto
    const nuevoEstado = {}
    resultados.forEach(r => {
      if (r && typeof r.mesa !== 'undefined') {
        nuevoEstado[r.mesa] = true
      }
    })
    
    // Actualizar el estado de forma atómica
    mesasRegistradas.value = nuevoEstado
    
    console.log('Estado de mesas registradas actualizado:', mesasRegistradas.value)
    
    // Si todas las mesas están registradas, habilitar el botón de cerrar partida
    if (todasMesasRegistradas.value) {
      console.log('Todas las mesas han sido registradas')
    }
  } catch (error) {
    console.error('Error al verificar mesas registradas:', error)
    mostrarError('Error al verificar mesas registradas: ' + error.message)
  }
}

// Watchers para actualizar el estado
watch(() => campeonatoSeleccionado.value?.partida_actual, async (newPartida, oldPartida) => {
  if (newPartida !== oldPartida && newPartida !== undefined) {
    console.log('Partida actual del campeonato cambió:', newPartida)
    partidaActual.value = newPartida
    try {
      await cargarMesas()
    } catch (error) {
      console.error('Error al cargar mesas después de cambio de partida:', error)
    }
  }
})

watch(() => partidaActual.value, async (newPartida, oldPartida) => {
  if (newPartida !== oldPartida && newPartida !== undefined) {
    console.log('Partida actual cambió:', newPartida)
    try {
      await cargarMesas()
    } catch (error) {
      console.error('Error al cargar mesas después de cambio de partida:', error)
    }
  }
})

// Función para recargar el estado del campeonato
const recargarEstadoCampeonato = async () => {
  try {
    if (!campeonatoId.value) {
      console.error('No hay ID de campeonato para recargar')
      router.push('/campeonatos')
      return false
    }

    console.log('Intentando recargar estado del campeonato:', campeonatoId.value)
    const timestamp = new Date().getTime()
    const response = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId.value}?t=${timestamp}`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Error en la respuesta del servidor:', {
        status: response.status,
        statusText: response.statusText,
        errorText
      })
      
      if (response.status === 404) {
        console.log('Campeonato no encontrado, redirigiendo...')
        localStorage.removeItem('campeonatoSeleccionado')
        router.push('/campeonatos')
        return false
      }
      
      throw new Error(`Error al obtener campeonato: ${response.status} - ${errorText}`)
    }
    
    const data = await response.json()
    console.log('Datos del campeonato recibidos:', data)
    
    if (!data || !data.id) {
      throw new Error('Datos del campeonato inválidos')
    }
    
    // Actualizar el estado de forma atómica
    const actualizarEstado = () => {
      campeonatoSeleccionado.value = data
      partidaActual.value = data.partida_actual || 0
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(data))
    }
    
    // Ejecutar la actualización en el siguiente tick para evitar problemas de timing
    await nextTick(actualizarEstado)
    
    console.log('Estado del campeonato actualizado:', {
      id: data.id,
      partida_actual: data.partida_actual,
      nombre: data.nombre
    })
    
    return true
  } catch (error) {
    console.error('Error al recargar estado del campeonato:', error)
    mostrarError(`Error al recargar estado del campeonato: ${error.message}`)
    return false
  }
}

const verificarCampeonato = async () => {
  if (!campeonatoId.value) {
    // Intentar obtener el ID del campeonato del localStorage
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      try {
        const campeonato = JSON.parse(campeonatoGuardado)
        campeonatoId.value = campeonato.id.toString()
      } catch (error) {
        console.error('Error al parsear campeonato del localStorage:', error)
        localStorage.removeItem('campeonatoSeleccionado')
        router.push('/campeonatos')
        return false
      }
    } else {
      // Si no hay campeonato guardado, redirigir a la página de campeonatos
      console.log('No hay campeonato guardado en localStorage')
      router.push('/campeonatos')
      return false
    }
  }
  
  try {
    console.log('Verificando campeonato:', campeonatoId.value)
    // Recargar el estado del campeonato primero
    const success = await recargarEstadoCampeonato()
    if (!success) {
      console.error('Error al recargar estado del campeonato')
      return false
    }

    console.log('Estado del campeonato recargado - Partida actual:', partidaActual.value)
    
    // Cargar las mesas solo si tenemos la partida actual
    if (partidaActual.value) {
      await cargarMesas()
      await verificarMesasRegistradas()
      return true
    } else {
      console.error('No se pudo obtener la partida actual')
      return false
    }
  } catch (error) {
    console.error('Error en verificarCampeonato:', error)
    mostrarError(`Error al verificar campeonato: ${error.message}`)
    return false
  }
}

// Función para recargar todos los datos
const recargarDatos = async () => {
  console.log('Recargando todos los datos...')
  try {
    // Limpiar el caché de localStorage para forzar una recarga fresca
    localStorage.removeItem('jugadoresActivos')
    
    const campeonatoVerificado = await verificarCampeonato()
    if (!campeonatoVerificado) {
      console.log('No se pudo verificar el campeonato, deteniendo recarga de datos')
      return
    }
    
    await Promise.all([
      cargarMesas(),
      verificarMesasRegistradas()
    ])
    
    console.log('Datos recargados exitosamente')
  } catch (error) {
    console.error('Error al recargar datos:', error)
    mostrarError('Error al recargar datos: ' + error.message)
  }
}

const iniciarIntervaloVerificacion = () => {
  // Limpiar intervalo existente si hay uno
  if (intervaloVerificacion.value) {
    clearInterval(intervaloVerificacion.value)
  }
  // Crear nuevo intervalo
  intervaloVerificacion.value = setInterval(verificarMesasRegistradas, 30000)
}

// Watcher para el ID del campeonato
watch(() => campeonatoId.value, () => {
  iniciarIntervaloVerificacion()
})

onMounted(async () => {
  try {
    await recargarDatos()
    
    // Escuchar eventos de actualización del ranking
    window.addEventListener('ranking-update', verificarMesasRegistradas)
    
    // Añadir listener para el evento visibilitychange
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible') {
        console.log('Vista de registro de mesas activada, recargando datos...')
        await recargarDatos()
      }
    })
    
    // Iniciar el intervalo de verificación
    iniciarIntervaloVerificacion()
  } catch (error) {
    console.error('Error durante la inicialización del componente:', error)
    mostrarError('Error al inicializar: ' + error.message)
  }
})

onUnmounted(() => {
  // Limpiar el intervalo
  if (intervaloVerificacion.value) {
    clearInterval(intervaloVerificacion.value)
  }
  
  window.removeEventListener('ranking-update', verificarMesasRegistradas)
  document.removeEventListener('visibilitychange', async () => {
    if (document.visibilityState === 'visible') {
      await recargarDatos()
    }
  })
  window.removeEventListener('jugador-actualizado', async () => {
    await recargarDatos()
  })
  window.removeEventListener('popstate', async () => {
    await recargarDatos()
  })
  window.removeEventListener('jugador-desactivado', async () => {
    await recargarDatos()
  })
})

const cargarResultadoMesa = async (mesa) => {
  try {
    const response = await fetch(`http://localhost:8000/api/resultados/mesa/${campeonatoId.value}/${partidaActual.value}/${mesa.numeroMesa}`)
    if (response.ok) {
      const resultados = await response.json()
      console.log('Resultados obtenidos:', resultados)
      if (resultados.length > 0) {
        // Devolver los resultados directamente como array
        return resultados
      }
    }
  } catch (error) {
    console.error('Error al cargar resultado de mesa:', error)
  }
  return null
}

const abrirModificacion = async (mesa) => {
  console.log('Iniciando abrirModificacion para mesa:', mesa)
  
  try {
    // Primero establecer la mesa seleccionada
    mesaSeleccionada.value = { 
      ...mesa,
      esUltimaMesa: mesa.numeroMesa === Math.max(...mesas.value.map(m => m.numeroMesa))
    }
    
    // Luego cargar el resultado existente si ya hay uno registrado
    if (mesasRegistradas.value[mesa.numeroMesa]) {
      const resultados = await cargarResultadoMesa(mesa)
      console.log('Resultados cargados:', resultados)
      resultadoExistente.value = resultados
    } else {
      resultadoExistente.value = null
    }

    // Asegurarse de que los valores necesarios estén definidos
    console.log('Estado antes de abrir popup:', {
      mesaSeleccionada: mesaSeleccionada.value,
      resultadoExistente: resultadoExistente.value,
      campeonatoId: campeonatoId.value,
      partidaActual: partidaActual.value
    })

    // Finalmente mostrar el popup
    showPopup.value = true
  } catch (error) {
    console.error('Error al abrir modificación:', error)
    alert('Error al cargar los resultados de la mesa')
  }
}

const onResultadoGuardado = async (resultado) => {
  try {
    console.log('Resultado guardado:', resultado)
    
    // Actualizar directamente el estado de la mesa registrada
    mesasRegistradas.value = {
      ...mesasRegistradas.value,
      [resultado.mesa]: true
    }
    
    // Recargar los datos completos
    await cargarMesas()
    await verificarMesasRegistradas()
    
    // Disparar evento para actualizar el ranking
    window.dispatchEvent(new Event('ranking-update'))
    
    console.log('Estado actualizado después de guardar - Mesas registradas:', mesasRegistradas.value)
  } catch (error) {
    console.error('Error al actualizar estado después de guardar:', error)
  }
}

// Función para cerrar la partida actual
const cerrarPartidaActual = async () => {
  try {
    const timestamp = new Date().getTime()
    const response = await fetch(`http://localhost:8000/api/partidas/cerrar/${campeonatoId.value}/${partidaActual.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })

    if (!response.ok) {
      throw new Error(`Error al cerrar la partida: ${response.status}`)
    }

    const data = await response.json()
    
    // Recargar el estado del campeonato
    await recargarEstadoCampeonato()
    
    // Solo cambiar a la vista de podium si el campeonato está finalizado
    if (data.mensaje === "Campeonato finalizado") {
      if (ventanaSecundaria.value && !ventanaSecundaria.value.closed) {
        ventanaSecundaria.value.location.href = `/resultados/podium/${campeonatoId.value}`
      } else {
        ventanaSecundaria.value = window.open(
          `/resultados/podium/${campeonatoId.value}`,
          'VisualizacionSecundaria',
          'width=1024,height=768,menubar=no,toolbar=no,location=no,status=no'
        )
      }
    }
    
    // Recargar las mesas para la nueva partida
    await cargarMesas()
    
    // Mostrar mensaje de éxito
    mostrarExito('Partida cerrada correctamente')
  } catch (error) {
    console.error('Error al cerrar la partida:', error)
    mostrarError('Error al cerrar la partida: ' + error.message)
  }
}

// Función para mostrar mensaje de éxito
const mostrarExito = (mensaje) => {
  // Implementar según el sistema de notificaciones que uses
  console.log('Éxito:', mensaje)
}

// Función para mostrar mensaje de error
const mostrarError = (mensaje) => {
  // Implementar según el sistema de notificaciones que uses
  console.error('Error:', mensaje)
}

// Función para cambiar la vista en la ventana secundaria
const cambiarVista = (vista) => {
  vistaSecundaria.value = vista
  if (!ventanaSecundaria.value || ventanaSecundaria.value.closed) {
    abrirVentanaSecundaria(vista)
  } else {
    // Actualizar la URL de la ventana existente con la partida actual
    const ruta = vista === 'ranking' 
      ? `/resultados/ranking/${campeonatoId.value}?partida=${partidaActual.value}`
      : `/mesas/asignacion/${campeonatoId.value}`
    ventanaSecundaria.value.location.href = ruta
  }
}

// Función para abrir la ventana secundaria
const abrirVentanaSecundaria = (vista) => {
  // Verificar si ya existe una ventana secundaria guardada
  const ventanaGuardada = localStorage.getItem('ventanaSecundaria')
  if (ventanaGuardada) {
    const ventanaExistente = window.open('', 'VisualizacionSecundaria')
    if (ventanaExistente && !ventanaExistente.closed) {
      ventanaSecundaria.value = ventanaExistente
      const ruta = vista === 'ranking' 
        ? `/resultados/ranking/${campeonatoId.value}?partida=${partidaActual.value}`
        : `/mesas/asignacion/${campeonatoId.value}`
      ventanaSecundaria.value.location.href = ruta
      return
    }
  }

  const ruta = vista === 'ranking' 
    ? `/resultados/ranking/${campeonatoId.value}?partida=${partidaActual.value}`
    : `/mesas/asignacion/${campeonatoId.value}`
    
  // Abrir nueva ventana si no existe
  ventanaSecundaria.value = window.open(
    ruta,
    'VisualizacionSecundaria',
    'width=1024,height=768,menubar=no,toolbar=no,location=no,status=no'
  )
  
  // Guardar referencia en localStorage
  if (ventanaSecundaria.value) {
    localStorage.setItem('ventanaSecundaria', 'true')
  }
}
</script>

<template>
  <div class="registro-mesas-container">
    <div class="header-section">
      <div class="header-left">
        <h2>Registro de Resultados</h2>
        <div class="partida-info">Partida {{ partidaActual }}</div>
      </div>
      <div class="header-right">
        <div class="visualizacion-control">
          <button 
            @click="cambiarVista('mesas')" 
            class="btn-visualizacion"
            :class="{ active: vistaSecundaria === 'mesas' }"
          >
            Ver Asignación
          </button>
          <button 
            @click="cambiarVista('ranking')" 
            class="btn-visualizacion"
            :class="{ active: vistaSecundaria === 'ranking' }"
          >
            Ver Ranking
          </button>
        </div>
        <div class="actions">
          <button 
            @click="cerrarPartidaActual" 
            class="btn-cerrar-partida"
            :disabled="!todasMesasRegistradas"
            :title="!todasMesasRegistradas ? 'Debe registrar los resultados de todas las mesas para cerrar la partida' : textoCerrarPartida"
          >
            {{ textoCerrarPartida }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="mesas-section">
      <h3>Mesas</h3>
      <div class="mesas-grid">
        <div v-for="mesa in mesas" :key="mesa.numeroMesa" class="mesa-card">
          <div class="mesa-header">
            <h4>Mesa {{ mesa.numeroMesa }}</h4>
            <div 
              :class="['estado-registro', mesasRegistradas[mesa.numeroMesa] ? 'registrado' : 'pendiente']"
              :title="mesasRegistradas[mesa.numeroMesa] ? 'Mesa finalizada' : 'Pendiente de registro'"
            >
              {{ mesasRegistradas[mesa.numeroMesa] ? 'Finalizada' : 'Pendiente' }}
            </div>
          </div>
          <div class="parejas-container">
            <div class="pareja">
              <div class="pareja-header">Pareja 1</div>
              <div class="jugadores">
                <template v-if="mesasRegistradas[mesa.numeroMesa]">
                  <!-- Si la mesa está registrada, mostrar todos los jugadores -->
                  <div v-if="mesa.pareja1?.jugador1" 
                       :class="['jugador', { 'inactivo': !mesa.pareja1.jugador1.activo }]">
                    {{ mesa.pareja1.jugador1.id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
                  </div>
                  <div class="jugador-separator" v-if="mesa.pareja1?.jugador1 && mesa.pareja1?.jugador2">/</div>
                  <div v-if="mesa.pareja1?.jugador2" 
                       :class="['jugador', { 'inactivo': !mesa.pareja1.jugador2.activo }]">
                    {{ mesa.pareja1.jugador2.id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
                  </div>
                </template>
                <template v-else>
                  <!-- Si la mesa no está registrada, mostrar todos los jugadores independientemente de su estado -->
                  <div v-if="mesa.pareja1?.jugador1" class="jugador" :class="{ 'inactivo': !mesa.pareja1.jugador1.activo }">
                    {{ mesa.pareja1.jugador1.id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
                  </div>
                  <div class="jugador-separator" v-if="mesa.pareja1?.jugador1 && mesa.pareja1?.jugador2">/</div>
                  <div v-if="mesa.pareja1?.jugador2" class="jugador" :class="{ 'inactivo': !mesa.pareja1.jugador2.activo }">
                    {{ mesa.pareja1.jugador2.id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
                  </div>
                  <div class="jugador-incompleto" v-if="!mesa.pareja1?.jugador1 && !mesa.pareja1?.jugador2">
                    Pareja incompleta
                  </div>
                </template>
              </div>
            </div>
            <div class="vs">vs</div>
            <div class="pareja">
              <div class="pareja-header">Pareja 2</div>
              <div class="jugadores">
                <template v-if="mesasRegistradas[mesa.numeroMesa]">
                  <!-- Si la mesa está registrada, mostrar todos los jugadores -->
                  <div v-if="mesa.pareja2?.jugador1" 
                       :class="['jugador', { 'inactivo': !mesa.pareja2.jugador1.activo }]">
                    {{ mesa.pareja2.jugador1.id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
                  </div>
                  <div class="jugador-separator" v-if="mesa.pareja2?.jugador1 && mesa.pareja2?.jugador2">/</div>
                  <div v-if="mesa.pareja2?.jugador2" 
                       :class="['jugador', { 'inactivo': !mesa.pareja2.jugador2.activo }]">
                    {{ mesa.pareja2.jugador2.id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
                  </div>
                </template>
                <template v-else>
                  <!-- Si la mesa no está registrada, mostrar todos los jugadores independientemente de su estado -->
                  <div v-if="mesa.pareja2?.jugador1" class="jugador" :class="{ 'inactivo': !mesa.pareja2.jugador1.activo }">
                    {{ mesa.pareja2.jugador1.id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
                  </div>
                  <div class="jugador-separator" v-if="mesa.pareja2?.jugador1 && mesa.pareja2?.jugador2">/</div>
                  <div v-if="mesa.pareja2?.jugador2" class="jugador" :class="{ 'inactivo': !mesa.pareja2.jugador2.activo }">
                    {{ mesa.pareja2.jugador2.id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
                  </div>
                  <div class="jugador-incompleto" v-if="!mesa.pareja2?.jugador1 && !mesa.pareja2?.jugador2">
                    Pareja incompleta
                  </div>
                </template>
              </div>
            </div>
          </div>
          <div class="mesa-actions">
            <button 
              @click="abrirModificacion(mesa)" 
              class="btn-registrar"
              :disabled="mesasRegistradas[mesa.numeroMesa] && esMesaIncompleta(mesa)"
              :style="{ '--button-color': mesasRegistradas[mesa.numeroMesa] ? '#2196F3' : '#4CAF50', '--button-hover-color': mesasRegistradas[mesa.numeroMesa] ? '#1976D2' : '#45a049' }"
              :title="mesasRegistradas[mesa.numeroMesa] && esMesaIncompleta(mesa) ? 'No se pueden modificar los resultados de mesas incompletas' : ''"
            >
              {{ mesasRegistradas[mesa.numeroMesa] ? 'Modificar' : 'Registrar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <ResultadoMesaPopup 
      v-if="showPopup"
      :show="showPopup" 
      :mesa="mesaSeleccionada"
      :campeonatoId="campeonatoId"
      :partidaActual="partidaActual"
      :resultadoExistente="resultadoExistente"
      @close="showPopup = false"
      @resultadoRegistrado="onResultadoGuardado"
    />
  </div>
</template>

<style scoped>
.registro-mesas-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .registro-mesas-container {
    padding: 10px;
  }
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  flex-wrap: wrap;
  gap: 15px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.header-left h2 {
  margin: 0;
  color: #2c3e50;
}

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
  padding: 5px 10px;
  background-color: #e8f5e9;
  border-radius: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.visualizacion-control {
  display: flex;
  gap: 10px;
}

.btn-visualizacion {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #87CEEB; /* Azul cielo */
  color: white;
}

.btn-visualizacion:hover {
  opacity: 0.9;
}

.btn-visualizacion.active {
  background-color: #00008B; /* Azul oscuro */
}

.actions {
  display: flex;
  justify-content: flex-end; /* Alinea el botón a la derecha */
}

.btn-cerrar-partida {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-weight: 800;
  font-size: 1.1em;
  letter-spacing: 0.5px;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.3s ease;
}

.btn-cerrar-partida:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.btn-cerrar-partida:disabled {
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
  opacity: 0.7;
}

.mesas-section {
  margin-top: 30px;
}

.mesas-section h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.mesas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.mesa-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.mesa-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.mesa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.mesa-header h4 {
  margin: 0;
  color: #2c3e50;
}

.estado-registro {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: bold;
}

.registrado {
  background-color: #dc3545;  /* Rojo */
  color: white;
}

.pendiente {
  background-color: #FFA726;  /* Naranja para pendiente */
  color: white;
}

.parejas-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pareja {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
}

.pareja-header {
  font-weight: bold;
  margin-bottom: 8px;
  color: #4CAF50;
}

.vs {
  text-align: center;
  font-weight: bold;
  margin: 5px 0;
  color: #666;
}

.jugadores {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.jugador {
  flex: 1;
  min-width: 150px;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jugador-separator {
  color: #666;
}

.mesa-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.btn-registrar {
  background-color: var(--button-color, #4CAF50);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-registrar:hover {
  background-color: var(--button-hover-color, #45a049);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
  .jugador {
    min-width: 120px;
    font-size: 0.85em;
  }
}

@media (max-width: 576px) {
  .jugadores {
    flex-direction: column;
    align-items: stretch;
  }
  
  .jugador {
    width: 100%;
  }
  
  .jugador-separator {
    display: none;
  }
}

/* Estilos globales para asegurar que el popup sea responsive */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 20px;
}

@media (max-width: 576px) {
  .popup-content {
    width: 95%;
    padding: 15px;
  }
}

.jugador-incompleto {
  color: #dc3545;
  font-style: italic;
  font-size: 0.9em;
  padding: 4px 8px;
  background-color: #f8d7da;
  border-radius: 4px;
  margin-top: 4px;
  width: 100%;
  text-align: center;
}

.jugador.inactivo {
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dc3545;
  font-style: italic;
}

.jugador.inactivo::after {
  content: " (Inactivo)";
  color: #dc3545;
  font-size: 0.9em;
  font-weight: bold;
}

.info-message {
  font-size: 0.9em;
  color: #666;
  margin-top: 0.5rem;
  text-align: center;
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.btn-registrar:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #cccccc !important;
}
</style> 