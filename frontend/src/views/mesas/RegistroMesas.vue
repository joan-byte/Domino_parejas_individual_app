<template>
  <div class="registro-mesas">
    <div class="header">
      <div class="header-left">
        <h2>Registro de Mesas</h2>
        <div class="visualizacion-control">
          <button
            class="btn-visualizacion"
            :class="{ active: vistaSecundaria === 'ranking' }"
            @click="cambiarVista('ranking')"
          >
            Ranking
          </button>
          <button
            class="btn-visualizacion"
            :class="{ active: vistaSecundaria === 'mesas' }"
            @click="cambiarVista('mesas')"
          >
            Mesas
          </button>
        </div>
      </div>
      <div class="header-right">
        <div class="partida-info">Partida {{ partidaActual }}</div>
        <button
          class="btn-cerrar-partida"
          :disabled="!todasMesasRegistradas"
          @click="cerrarPartida"
        >
          {{ textoCerrarPartida }}
        </button>
      </div>
    </div>
    
    <div class="mesas-grid" v-if="mesasConParejas.length > 0">
      <div class="mesa-card" v-for="mesa in mesasConParejas" :key="mesa.numeroMesa">
        <div class="mesa-header">
          <h3>Mesa {{ mesa.numeroMesa }}</h3>
        </div>
        
        <div class="parejas-container">
          <div class="parejas-row">
            <div class="pareja-info">
              <span class="pareja-label">Pareja 1:</span>
              <div class="jugadores">
                <span class="jugador" v-if="mesa.pareja1?.jugador1">
                  {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
                </span>
                <template v-if="mesa.pareja1?.jugador2">
                  <span class="jugador-separator">/</span>
                  <span class="jugador">
                    {{ mesa.pareja1.jugador2_id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
                  </span>
                </template>
              </div>
            </div>
            <div class="separator">vs</div>
            <div class="pareja-info">
              <span class="pareja-label">Pareja 2:</span>
              <div class="jugadores">
                <span class="jugador" v-if="mesa.pareja2?.jugador1">
                  {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
                </span>
                <template v-if="mesa.pareja2?.jugador2">
                  <span class="jugador-separator">/</span>
                  <span class="jugador">
                    {{ mesa.pareja2.jugador2_id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
                  </span>
                </template>
              </div>
            </div>
          </div>
          <div class="actions">
            <button 
              :class="{
                'btn-registrar': true,
                'btn-primary': !mesasRegistradas[mesa.numeroMesa],
                'btn-secondary': mesasRegistradas[mesa.numeroMesa]
              }"
              @click="abrirRegistro(mesa)"
              :disabled="mesasRegistradas[mesa.numeroMesa]"
            >
              Registrar
            </button>
            <button 
              :class="{
                'btn-modificar': true,
                'btn-primary': mesasRegistradas[mesa.numeroMesa],
                'btn-secondary': !mesasRegistradas[mesa.numeroMesa]
              }"
              @click="abrirModificacion(mesa)"
              :disabled="!mesasRegistradas[mesa.numeroMesa]"
            >
              Modificar
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>No hay mesas asignadas todavía.</p>
    </div>

    <ResultadoMesaPopup
      v-model:show="showPopup"
      :mesa="mesaSeleccionada"
      :campeonato-id="campeonatoId"
      :partida-actual="partidaActual"
      :resultado-existente="resultadoExistente"
      :es-ultima-mesa="mesaSeleccionada?.esUltimaMesa"
      @close="cerrarPopup"
      @resultado-registrado="onResultadoRegistrado"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventBus } from '@vueuse/core'
import ResultadoMesaPopup from '@/components/ResultadoMesaPopup.vue'
import router from '@/router'

const route = useRoute()
const campeonatoId = parseInt(route.params.campeonatoId)
const mesas = ref([])
const mesasRegistradas = ref({})
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(null)
const mesaSeleccionada = ref(null)
const showPopup = ref(false)
const esUltimaPartida = ref(false)
const resultadoExistente = ref(null)

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

// Añadir nuevas variables para el control de visualización
const vistaSecundaria = ref('ranking')
const ventanaSecundaria = ref(null)

const abrirRegistro = (mesa) => {
  mesaSeleccionada.value = mesa
  // Verificar si es la última mesa
  const esUltima = mesa.numeroMesa === Math.max(...mesas.value.map(m => m.numeroMesa))
  mesaSeleccionada.value.esUltimaMesa = esUltima
  resultadoExistente.value = null // Aseguramos que resultadoExistente sea null para nuevo registro
  showPopup.value = true
}

const cerrarPopup = () => {
  showPopup.value = false
  mesaSeleccionada.value = null
  resultadoExistente.value = null
}

const onResultadoRegistrado = () => {
  verificarMesasRegistradas()
}

const verificarMesasRegistradas = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/resultados/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (response.ok) {
      const resultados = await response.json()
      // Agrupar resultados por mesa
      const mesasReg = {}
      resultados.forEach(resultado => {
        mesasReg[resultado.mesa] = true
      })
      mesasRegistradas.value = mesasReg
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const cargarMesas = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (!response.ok) {
      throw new Error(`Error al cargar las mesas: ${response.statusText}`)
    }
    const data = await response.json()
    
    // Procesar los datos para agrupar las parejas por mesa
    const mesasTemp = new Map()
    
    data.forEach(pareja => {
      const mesaNum = pareja.mesa
      if (!mesasTemp.has(mesaNum)) {
        mesasTemp.set(mesaNum, {
          numeroMesa: mesaNum,
          pareja1: null,
          pareja2: null
        })
      }
      
      const mesa = mesasTemp.get(mesaNum)
      if (pareja.numero_pareja === 1) {
        mesa.pareja1 = pareja
      } else if (pareja.numero_pareja === 2) {
        mesa.pareja2 = pareja
      }
    })
    
    // Convertir el Map a un array y ordenar por número de mesa
    mesas.value = Array.from(mesasTemp.values())
      .sort((a, b) => a.numeroMesa - b.numeroMesa)
    
    await verificarMesasRegistradas()
  } catch (error) {
    console.error('Error al cargar las mesas:', error)
    mesas.value = []
  }
}

const mesasConParejas = computed(() => {
  return mesas.value || []
})

const todasMesasRegistradas = computed(() => {
  if (!mesasConParejas.value.length) return false
  
  // Verificar que todas las mesas tienen resultados registrados
  const todasRegistradas = mesasConParejas.value.every(mesa => {
    const tieneResultado = mesasRegistradas.value[mesa.numeroMesa] === true
    console.log(`Mesa ${mesa.numeroMesa}: ${tieneResultado ? 'tiene resultado' : 'no tiene resultado'}`)
    return tieneResultado
  })
  
  console.log('¿Todas las mesas registradas?:', todasRegistradas)
  return todasRegistradas
})

const cargarResultadoMesa = async (mesa) => {
  try {
    const response = await fetch(`http://localhost:8000/api/resultados/mesa/${campeonatoId}/${partidaActual.value}/${mesa.numeroMesa}`)
    if (response.ok) {
      const resultados = await response.json()
      if (resultados.length > 0) {
        // Obtener datos completos de ambas parejas
        const pareja1 = resultados.find(r => r.jugador === 1)
        const pareja2 = resultados.find(r => r.jugador === 3)
        
        // Incluir todos los campos necesarios para la actualización
        return {
          campeonato_id: campeonatoId,
          partida: partidaActual.value,
          mesa: mesa.numeroMesa,
          es_ultima_mesa: mesa.esUltimaMesa,
          jugador1_id: mesa.pareja1?.jugador1_id,
          jugador2_id: mesa.pareja1?.jugador2_id,
          jugador3_id: mesa.pareja2?.jugador1_id,
          jugador4_id: mesa.pareja2?.jugador2_id,
          puntos_pareja1: pareja1?.PT || 0,
          puntos_pareja2: pareja2?.PT || 0,
          manos_ganadas_pareja1: pareja1?.MG || 0,
          manos_ganadas_pareja2: pareja2?.MG || 0
        }
      }
    }
  } catch (error) {
    console.error('Error al cargar resultado de mesa:', error)
  }
  return null
}

const abrirModificacion = async (mesa) => {
  mesaSeleccionada.value = mesa
  // Verificar si es la última mesa
  const esUltima = mesa.numeroMesa === Math.max(...mesas.value.map(m => m.numeroMesa))
  mesaSeleccionada.value.esUltimaMesa = esUltima
  // Primero establecemos resultadoExistente a null antes de cargar el nuevo resultado
  resultadoExistente.value = null
  resultadoExistente.value = await cargarResultadoMesa(mesa)
  showPopup.value = true
}

const onResultadoGuardado = async (resultado) => {
  try {
    // Actualizar directamente el estado de la mesa registrada
    mesasRegistradas.value = {
      ...mesasRegistradas.value,
      [resultado.mesa]: resultado.registrado
    }
    
    // Recargar los datos completos
    await cargarMesas()
    await verificarMesasRegistradas()
    
    // Disparar evento para actualizar el ranking
    window.dispatchEvent(new Event('ranking-update'))
    
    console.log('Estado actualizado después de guardar:', mesasRegistradas.value)
  } catch (error) {
    console.error('Error al actualizar estado después de guardar:', error)
  }
}

const cerrarPartida = async () => {
  if (!todasMesasRegistradas.value) return

  try {
    // Recargar el estado actual del campeonato
    await recargarEstadoCampeonato()

    // 1. Cerrar la partida actual
    const responseCierre = await fetch(`http://localhost:8000/api/parejas-partida/partidas/cerrar/${campeonatoId}/${partidaActual.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!responseCierre.ok) {
      const errorData = await responseCierre.json()
      throw new Error(errorData.detail || 'Error al cerrar la partida')
    }

    const datosResponse = await responseCierre.json()
    const nuevaPartida = datosResponse.nueva_partida

    // Si es la última partida, finalizar el campeonato
    if (esUltimaPartida.value) {
      const responseFinalizar = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}/finalizar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!responseFinalizar.ok) {
        throw new Error('Error al finalizar el campeonato')
      }

      alert('Campeonato finalizado correctamente')
      
      // Actualizar la ventana secundaria para mostrar el podium
      if (ventanaSecundaria.value && !ventanaSecundaria.value.closed) {
        ventanaSecundaria.value.location.href = `/resultados/podium/${campeonatoId}`
      }
      
      // Limpiar localStorage y redirigir la ventana principal
      localStorage.clear()
      router.push('/')
      return
    }

    // 2. Obtener el ranking actualizado
    const responseRanking = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
    if (!responseRanking.ok) {
      throw new Error('Error al obtener el ranking')
    }
    const ranking = await responseRanking.json()

    // 3. Crear las nuevas parejas según el ranking para la siguiente partida
    try {
      const responseNuevasParejas = await fetch(`http://localhost:8000/api/parejas-partida/siguiente-partida/${campeonatoId}/${nuevaPartida - 1}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          ranking,
          partida: nuevaPartida
        })
      })

      if (!responseNuevasParejas.ok) {
        const errorData = await responseNuevasParejas.json()
        throw new Error(errorData.detail || 'Error al asignar nuevas parejas')
      }

      // Recargar el estado del campeonato después de crear las nuevas parejas
      await recargarEstadoCampeonato()

      alert('Partida cerrada y nuevas parejas asignadas correctamente')
      
      // Disparar evento para actualizar la asignación de mesas
      window.dispatchEvent(new Event('update-asignacion-mesas'))
      
      // Actualizar la ventana secundaria
      if (ventanaSecundaria.value && !ventanaSecundaria.value.closed) {
        ventanaSecundaria.value.location.href = `/mesas/asignacion/${campeonatoId}`
        vistaSecundaria.value = 'mesas'
      }
      
      // Recargar los datos en la ventana principal sin navegar
      await cargarMesas()

    } catch (error) {
      console.error('Error al crear nuevas parejas:', error)
      throw new Error('Error al asignar nuevas parejas: ' + error.message)
    }
  } catch (error) {
    console.error('Error:', error)
    alert('Error al cerrar la partida: ' + error.message)
  }
}

// Función para cambiar la vista en la ventana secundaria
const cambiarVista = (vista) => {
  vistaSecundaria.value = vista
  if (!ventanaSecundaria.value || ventanaSecundaria.value.closed) {
    abrirVentanaSecundaria(vista)
  } else {
    // Actualizar la URL de la ventana existente con la partida actual
    const ruta = vista === 'ranking' 
      ? `/resultados/ranking/${campeonatoId}?partida=${partidaActual.value}`
      : `/mesas/asignacion/${campeonatoId}`
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
        ? `/resultados/ranking/${campeonatoId}?partida=${partidaActual.value}`
        : `/mesas/asignacion/${campeonatoId}`
      ventanaSecundaria.value.location.href = ruta
      return
    }
  }

  const ruta = vista === 'ranking' 
    ? `/resultados/ranking/${campeonatoId}?partida=${partidaActual.value}`
    : `/mesas/asignacion/${campeonatoId}`
    
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

// Función para forzar la recarga del estado del campeonato
const recargarEstadoCampeonato = async () => {
  try {
    // Obtener la última partida con parejas asignadas
    const responseUltimaPartida = await fetch(`http://localhost:8000/api/parejas-partida/ultima-partida/${campeonatoId}`)
    if (!responseUltimaPartida.ok) {
      throw new Error('Error al obtener la última partida')
    }
    const { ultima_partida } = await responseUltimaPartida.json()
    
    // Obtener el estado del campeonato
    const response = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!response.ok) {
      throw new Error('Error al obtener información del campeonato')
    }
    const campeonato = await response.json()
    console.log('Estado del campeonato recargado:', campeonato)
    
    // Asegurarnos de que la partida actual coincida con la última partida con parejas
    campeonatoSeleccionado.value = campeonato
    partidaActual.value = ultima_partida
    
    // Corregir el cálculo de última partida
    esUltimaPartida.value = ultima_partida === campeonato.numero_partidas
    
    console.log('Partida actual:', partidaActual.value)
    console.log('Número total de partidas:', campeonato.numero_partidas)
    console.log('Es última partida:', esUltimaPartida.value)
    
    // Actualizar la vista secundaria si existe
    if (ventanaSecundaria.value && !ventanaSecundaria.value.closed) {
      cambiarVista(vistaSecundaria.value)
    }
    
    await cargarMesas()
  } catch (error) {
    console.error('Error al recargar estado:', error)
    alert('Error al recargar el estado del campeonato')
  }
}

// Modificar onMounted para usar la nueva función
onMounted(async () => {
  try {
    // Limpiar todo el localStorage relacionado con el campeonato
    localStorage.clear()
    
    // Recargar el estado inicial
    await recargarEstadoCampeonato()
    
    // Verificar si ya existe una ventana secundaria
    const ventanaGuardada = localStorage.getItem('ventanaSecundaria')
    if (!ventanaGuardada) {
      abrirVentanaSecundaria('ranking')
    }
  } catch (error) {
    console.error('Error al cargar el campeonato:', error)
    alert('Error al cargar el campeonato: ' + error.message)
    router.push('/')
  }
})

// Eliminar el cierre de la ventana en onUnmounted
onUnmounted(() => {
  // No cerramos la ventana secundaria al desmontar
})

const textoCerrarPartida = computed(() => {
  return esUltimaPartida.value ? 'Cerrar Campeonato' : 'Cerrar Partida'
})
</script>

<style scoped>
.registro-mesas {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 60px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
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

.mesas-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

.mesa-card {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px 40px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.mesa-header {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.mesa-header h3 {
  margin: 0;
  color: #2c3e50;
  text-align: center;
}

.parejas-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.parejas-row {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  background-color: #f8f9fa;
  padding: 15px 0;
  border-radius: 4px;
  gap: 20px;
}

.pareja-info {
  display: flex;
  flex-direction: column;
  background-color: white;
  padding: 12px 15px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  width: calc(50% - 35px);
  margin: 0 15px;
  overflow: hidden;
}

.pareja-label {
  color: #4CAF50;
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
  margin-right: 8px;
}

.separator {
  font-weight: bold;
  color: #666;
  font-size: 1.1em;
  width: 30px;
  text-align: center;
  flex-shrink: 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #666;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #f0f0f0 !important;
  color: #666 !important;
}

.jugadores {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
}

.jugador {
  flex: 1;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 1em;
  white-space: nowrap;
  text-align: center;
}

.jugador-separator {
  color: #666;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 1rem;
  flex-shrink: 0;
}
</style> 