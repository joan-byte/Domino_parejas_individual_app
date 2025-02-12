<template>
  <div class="registro-mesas">
    <div class="header">
      <h2>Registro de Mesas</h2>
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
                <span class="jugador">
                  {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
                </span>
                <span class="jugador-separator">,</span>
                <span class="jugador">
                  {{ mesa.pareja1.jugador2_id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
                </span>
              </div>
            </div>
            <div class="separator">y</div>
            <div class="pareja-info">
              <span class="pareja-label">Pareja 2:</span>
              <div class="jugadores">
                <span class="jugador">
                  {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
                </span>
                <span class="jugador-separator">,</span>
                <span class="jugador">
                  {{ mesa.pareja2.jugador2_id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
                </span>
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
const partidaActual = ref(1)
const mesaSeleccionada = ref(null)
const showPopup = ref(false)
const esUltimaPartida = ref(false)
const resultadoExistente = ref(null)

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

const abrirRegistro = (mesa) => {
  mesaSeleccionada.value = mesa
  showPopup.value = true
}

const cerrarPopup = () => {
  showPopup.value = false
  mesaSeleccionada.value = null
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
    
    // Convertir el Map a un array y filtrar mesas incompletas
    mesas.value = Array.from(mesasTemp.values())
      .filter(mesa => mesa.pareja1 && mesa.pareja2)
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
        // Agrupar resultados por pareja
        const puntos_pareja1 = resultados.find(r => r.jugador === 1)?.PT || 0
        const puntos_pareja2 = resultados.find(r => r.jugador === 3)?.PT || 0
        return { puntos_pareja1, puntos_pareja2 }
      }
    }
  } catch (error) {
    console.error('Error al cargar resultado de mesa:', error)
  }
  return null
}

const abrirModificacion = async (mesa) => {
  mesaSeleccionada.value = mesa
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
    // Primero obtener el estado actual del campeonato
    const responseCampeonato = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!responseCampeonato.ok) {
      throw new Error('Error al obtener información del campeonato')
    }
    const campeonato = await responseCampeonato.json()
    
    // Actualizar el estado local con la información más reciente
    campeonatoSeleccionado.value = campeonato
    partidaActual.value = campeonato.partida_actual
    esUltimaPartida.value = partidaActual.value === campeonato.numero_partidas

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
      const responseNuevasParejas = await fetch(`http://localhost:8000/api/parejas-partida/parejas-partida/siguiente-partida/${campeonatoId}/${partidaActual.value}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          ranking,
          partida: nuevaPartida // Asegurarnos de usar la nueva partida
        })
      })

      if (!responseNuevasParejas.ok) {
        const errorData = await responseNuevasParejas.json()
        throw new Error(errorData.detail || 'Error al asignar nuevas parejas')
      }
    } catch (error) {
      console.error('Error al crear nuevas parejas:', error)
      throw new Error('Error al asignar nuevas parejas: ' + error.message)
    }

    // 4. Actualizar el localStorage con la nueva partida
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      const campeonato = JSON.parse(campeonatoGuardado)
      campeonato.partida_actual = nuevaPartida
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
    }

    alert('Partida cerrada y nuevas parejas asignadas correctamente')
    // 5. Redirigir a la página de asignación de mesas para la siguiente partida
    router.push(`/mesas/asignacion/${campeonatoId}`)
  } catch (error) {
    console.error('Error:', error)
    alert('Error al cerrar la partida: ' + error.message)
  }
}

onMounted(async () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    const campeonato = JSON.parse(campeonatoGuardado)
    campeonatoSeleccionado.value = campeonato
    partidaActual.value = campeonato.partida_actual || 1
    esUltimaPartida.value = partidaActual.value === campeonato.numero_partidas
    await cargarMesas()
  } else {
    console.error('No hay campeonato seleccionado')
  }
})

// Limpiar el event bus cuando el componente se desmonta
onUnmounted(() => {
  if (rankingBus) {
    rankingBus.off()
  }
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
  flex-wrap: nowrap;
  gap: 0.5rem;
}

.jugador {
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 1em;
  white-space: nowrap;
}

.jugador-separator {
  color: #666;
  font-weight: bold;
}
</style> 