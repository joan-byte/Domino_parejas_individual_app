<template>
  <div class="registro-mesas">
    <div class="header">
      <h2>Registro de Mesas</h2>
      <div class="header-right">
        <button 
          class="btn-cerrar-partida" 
          :disabled="!todasMesasRegistradas"
          :title="!todasMesasRegistradas ? 'Todas las mesas deben tener resultados registrados' : 'Cerrar la partida actual'"
          @click="cerrarPartida"
        >
          {{ textoCerrarPartida }}
        </button>
        <div class="partida-info">
          <span>Partida: {{ partidaActual }}</span>
        </div>
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
      :partida="partidaActual"
      :resultado-existente="resultadoExistente"
      @resultado-guardado="onResultadoGuardado"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ResultadoMesaPopup from '@/components/ResultadoMesaPopup.vue'

const route = useRoute()
const router = useRouter()
const campeonatoId = parseInt(route.params.campeonatoId)
const mesas = ref([])
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(1)
const mesasRegistradas = ref({})
const showPopup = ref(false)
const mesaSeleccionada = ref(null)
const resultadoExistente = ref(null)
const esUltimaPartida = computed(() => {
  return campeonatoSeleccionado.value && 
         partidaActual.value === campeonatoSeleccionado.value.numero_partidas
})

const textoCerrarPartida = computed(() => {
  return esUltimaPartida.value ? 'Cerrar Campeonato' : 'Cerrar Partida'
})

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
    console.log('Partida actual:', partidaActual.value)
  }
}

const cargarMesas = async () => {
  try {
    console.log('Cargando mesas para partida:', partidaActual.value)
    const response = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (response.ok) {
      const parejas = await response.json()
      console.log('Parejas recibidas:', parejas)
      
      // Agrupar parejas por mesa
      const mesasTemp = []
      const mesasProcesadas = new Set()
      
      parejas.forEach(pareja => {
        if (!mesasProcesadas.has(pareja.mesa)) {
          const pareja1 = parejas.find(p => p.mesa === pareja.mesa && p.numero_pareja === 1)
          const pareja2 = parejas.find(p => p.mesa === pareja.mesa && p.numero_pareja === 2)
          
          if (pareja1 && pareja2) {
            mesasTemp.push({
              numeroMesa: pareja.mesa,
              pareja1,
              pareja2
            })
            mesasProcesadas.add(pareja.mesa)
          }
        }
      })
      
      console.log('Mesas procesadas:', mesasTemp)
      mesas.value = mesasTemp
      await verificarMesasRegistradas()
    } else {
      console.error('Error al cargar las mesas:', response.statusText)
      mesas.value = []
    }
  } catch (error) {
    console.error('Error al cargar las mesas:', error)
    mesas.value = []
  }
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

const mesasConParejas = computed(() => {
  if (!mesas.value || !Array.isArray(mesas.value)) {
    return []
  }
  
  const mesasMap = new Map()
  
  mesas.value.forEach(mesa => {
    if (!mesasMap.has(mesa.numeroMesa)) {
      mesasMap.set(mesa.numeroMesa, {
        numeroMesa: mesa.numeroMesa,
        pareja1: mesa.pareja1,
        pareja2: mesa.pareja2
      })
    }
  })
  
  return Array.from(mesasMap.values())
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

const abrirRegistro = (mesa) => {
  mesaSeleccionada.value = mesa
  resultadoExistente.value = null
  showPopup.value = true
}

const abrirModificacion = async (mesa) => {
  mesaSeleccionada.value = mesa
  resultadoExistente.value = await cargarResultadoMesa(mesa)
  showPopup.value = true
}

const onResultadoGuardado = async () => {
  try {
    // Esperamos un momento para asegurar que los datos se han guardado en la BD
    await new Promise(resolve => setTimeout(resolve, 200))
    await verificarMesasRegistradas()
    console.log('Estado actualizado después de guardar:', mesasRegistradas.value)
  } catch (error) {
    console.error('Error al actualizar estado después de guardar:', error)
  }
}

const cerrarPartida = async () => {
  if (!todasMesasRegistradas.value) return

  try {
    // 1. Cerrar la partida actual
    const responseCierre = await fetch(`http://localhost:8000/api/partidas/cerrar/${campeonatoId}/${partidaActual.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!responseCierre.ok) {
      throw new Error('Error al cerrar la partida')
    }

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
    const responseRanking = await fetch(`http://localhost:8000/api/ranking/campeonato/${campeonatoId}`)
    if (!responseRanking.ok) {
      throw new Error('Error al obtener el ranking')
    }
    const ranking = await responseRanking.json()

    // 3. Crear las nuevas parejas según el ranking
    const nuevaPartida = partidaActual.value + 1
    const parejasPorRanking = []
    
    // Ordenar jugadores por ranking (PT descendente)
    const jugadoresOrdenados = ranking.sort((a, b) => b.PT - a.PT)
    
    // Crear parejas según el patrón: (1,3), (2,4), (5,7), (6,8), etc.
    for (let i = 0; i < jugadoresOrdenados.length; i += 4) {
      const mesa = Math.floor(i / 4) + 1
      
      // Pareja 1: jugador ranking 1 y 3 de cada grupo de 4
      if (i + 2 < jugadoresOrdenados.length) {
        parejasPorRanking.push({
          mesa: mesa,
          jugador1_id: jugadoresOrdenados[i].jugador_id,
          jugador2_id: jugadoresOrdenados[i + 2].jugador_id,
          partida: nuevaPartida
        })
      }
      
      // Pareja 2: jugador ranking 2 y 4 de cada grupo de 4
      if (i + 3 < jugadoresOrdenados.length) {
        parejasPorRanking.push({
          mesa: mesa,
          jugador1_id: jugadoresOrdenados[i + 1].jugador_id,
          jugador2_id: jugadoresOrdenados[i + 3].jugador_id,
          partida: nuevaPartida
        })
      }
    }

    // 4. Guardar las nuevas parejas
    const responseNuevasParejas = await fetch(`http://localhost:8000/api/parejas-partida/asignar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        campeonato_id: campeonatoId,
        partida: nuevaPartida,
        parejas: parejasPorRanking
      })
    })

    if (!responseNuevasParejas.ok) {
      throw new Error('Error al asignar nuevas parejas')
    }

    // 5. Actualizar el localStorage con la nueva partida
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      const campeonato = JSON.parse(campeonatoGuardado)
      campeonato.partida_actual = nuevaPartida
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
    }

    alert('Partida cerrada y nuevas parejas asignadas correctamente')
    // 6. Redirigir a la página de asignación de mesas para la siguiente partida
    router.push(`/mesas/asignacion/${campeonatoId}`)
  } catch (error) {
    console.error('Error:', error)
    alert('Error al cerrar la partida: ' + error.message)
  }
}

onMounted(() => {
  checkCampeonatoSeleccionado()
  cargarMesas()
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