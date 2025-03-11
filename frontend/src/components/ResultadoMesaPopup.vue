<template>
  <div class="popup-overlay" v-if="show">
    <div class="popup-content">
      <h3>Registro de Resultados - Mesa {{ mesa.numeroMesa }}</h3>
      
      <div v-if="esMesaIncompleta" class="mesa-incompleta-aviso">
        <div class="aviso-header">
          <i class="fas fa-exclamation-triangle"></i>
          <span>Mesa Incompleta</span>
        </div>
        <p>Esta mesa tiene jugadores inactivos y será procesada como incompleta.</p>
        <ul>
          <li>Los jugadores presentes recibirán puntos automáticos.</li>
          <li>Los campos están bloqueados para evitar modificaciones manuales.</li>
          <li>Los resultados se guardarán según el reglamento.</li>
        </ul>
      </div>
      
      <div class="resultados-container">
        <div class="pareja-resultados">
          <div class="pareja-info">
            <div class="jugador" v-if="mesa.pareja1?.jugador1?.activo">
              {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
            </div>
            <template v-if="mesa.pareja1?.jugador2?.activo">
              <div class="jugador-separator">/</div>
              <div class="jugador">
                {{ mesa.pareja1.jugador2_id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
              </div>
            </template>
          </div>
          <div class="puntos-row">
            <div class="input-group">
              <label for="pt-pareja1">PT:</label>
              <input 
                id="pt-pareja1"
                name="pt-pareja1"
                type="number" 
                v-model.number="puntosPareja1.PT" 
                min="0" 
                :max="campeonatoPM * 2"
                @input="calcularPuntos(1)"
                :disabled="esMesaIncompleta"
              >
            </div>
            <div class="input-group">
              <label for="mg-pareja1">MG:</label>
              <input 
                id="mg-pareja1"
                name="mg-pareja1"
                type="number" 
                v-model.number="puntosPareja1.MG" 
                min="0"
                max="20"
                :disabled="esMesaIncompleta"
              >
            </div>
            <div class="input-group">
              <label for="pv-pareja1">PV:</label>
              <input 
                id="pv-pareja1"
                name="pv-pareja1"
                type="number" 
                v-model.number="puntosPareja1.PV" 
                disabled
                :class="{ 'error': pvIguales }"
              >
            </div>
            <div class="input-group">
              <label for="pg-pareja1">PG:</label>
              <input 
                id="pg-pareja1"
                name="pg-pareja1"
                type="number" 
                v-model.number="puntosPareja1.PG" 
                disabled
              >
            </div>
            <div class="input-group">
              <label for="pc-pareja1">Dif.:</label>
              <input 
                id="pc-pareja1"
                name="pc-pareja1"
                type="number" 
                v-model.number="puntosPareja1.PC" 
                disabled
              >
            </div>
          </div>
        </div>

        <div class="separador">VS</div>

        <div class="pareja-resultados" v-if="tieneJugadoresActivosPareja2">
          <div class="pareja-info">
            <div class="jugador" v-if="mesa.pareja2?.jugador1?.activo">
              {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
            </div>
            <template v-if="mesa.pareja2?.jugador2?.activo">
              <div class="jugador-separator">/</div>
              <div class="jugador">
                {{ mesa.pareja2.jugador2_id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
              </div>
            </template>
          </div>
          <div class="puntos-row">
            <div class="input-group">
              <label for="pt-pareja2">PT:</label>
              <input 
                id="pt-pareja2"
                name="pt-pareja2"
                type="number" 
                v-model.number="puntosPareja2.PT" 
                min="0" 
                :max="campeonatoPM * 2"
                @input="calcularPuntos(2)"
                :disabled="esMesaIncompleta"
              >
            </div>
            <div class="input-group">
              <label for="mg-pareja2">MG:</label>
              <input 
                id="mg-pareja2"
                name="mg-pareja2"
                type="number" 
                v-model.number="puntosPareja2.MG" 
                min="0"
                max="20"
                :disabled="esMesaIncompleta"
              >
            </div>
            <div class="input-group">
              <label for="pv-pareja2">PV:</label>
              <input 
                id="pv-pareja2"
                name="pv-pareja2"
                type="number" 
                v-model.number="puntosPareja2.PV" 
                disabled
                :class="{ 'error': pvIguales }"
              >
            </div>
            <div class="input-group">
              <label for="pg-pareja2">PG:</label>
              <input 
                id="pg-pareja2"
                name="pg-pareja2"
                type="number" 
                v-model.number="puntosPareja2.PG" 
                disabled
              >
            </div>
            <div class="input-group">
              <label for="pc-pareja2">Dif.:</label>
              <input 
                id="pc-pareja2"
                name="pc-pareja2"
                type="number" 
                v-model.number="puntosPareja2.PC" 
                disabled
              >
            </div>
          </div>
        </div>
        <div class="pareja-resultados empty-pareja" v-else>
          <div class="no-jugadores-mensaje">
            No hay jugadores activos en la segunda pareja
          </div>
        </div>
      </div>

      <div class="error-message" v-if="pvIguales && !esMesaIncompleta">
        Los PV no pueden ser iguales en una mesa completa
      </div>

      <div class="actions">
        <button 
          @click="guardarResultados" 
          class="btn-guardar"
          :disabled="(!validarPuntos() && !esMesaIncompleta) || (esMesaIncompleta && props.resultadoExistente)"
        >
          {{ props.resultadoExistente ? 'Modificar' : 'Registrar' }}
        </button>
        <button @click="cerrar" class="btn-cancelar">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { useEventBus } from '@vueuse/core'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  mesa: {
    type: Object,
    required: true
  },
  campeonatoId: {
    type: [Number, String],
    required: true
  },
  partidaActual: {
    type: Number,
    required: true
  },
  resultadoExistente: {
    type: [Object, Array],
    default: null
  },
  esUltimaMesa: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'resultadoRegistrado'])

const puntosPareja1 = ref({ PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 })
const puntosPareja2 = ref({ PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 })
const campeonatoPM = ref(300)

const limpiarCampos = () => {
  puntosPareja1.value = { PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 }
  puntosPareja2.value = { PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 }
}

const cerrar = () => {
  limpiarCampos()
  emit('close')
}

const tieneJugadoresActivosPareja2 = computed(() => {
  return props.mesa.pareja2?.jugador1?.activo || props.mesa.pareja2?.jugador2?.activo
})

const esMesaIncompleta = computed(() => {
  if (!props.mesa) return false
  
  const jugadoresInactivos = [
    !props.mesa.pareja1?.jugador1?.activo,
    !props.mesa.pareja1?.jugador2?.activo,
    !props.mesa.pareja2?.jugador1?.activo,
    !props.mesa.pareja2?.jugador2?.activo
  ]

  return jugadoresInactivos.some(inactivo => inactivo === true || inactivo === undefined)
})

const jugadoresActivos = computed(() => {
  const jugadores = []
  
  if (props.mesa.pareja1?.jugador1?.activo) {
    jugadores.push({
      id: props.mesa.pareja1.jugador1_id,
      numero: 1,
      pareja: 1
    })
  }
  if (props.mesa.pareja1?.jugador2?.activo) {
    jugadores.push({
      id: props.mesa.pareja1.jugador2_id,
      numero: 2,
      pareja: 1
    })
  }
  
  if (props.mesa.pareja2?.jugador1?.activo) {
    jugadores.push({
      id: props.mesa.pareja2.jugador1_id,
      numero: 3,
      pareja: 2
    })
  }
  if (props.mesa.pareja2?.jugador2?.activo) {
    jugadores.push({
      id: props.mesa.pareja2.jugador2_id,
      numero: 4,
      pareja: 2
    })
  }
  
  return jugadores
})

const pvIguales = computed(() => {
  if (esMesaIncompleta.value) return false
  
  const mesaCompleta = props.mesa.pareja1?.jugador1?.activo && 
                      props.mesa.pareja1?.jugador2?.activo && 
                      props.mesa.pareja2?.jugador1?.activo && 
                      props.mesa.pareja2?.jugador2?.activo
                      
  return mesaCompleta && 
         puntosPareja1.value.PV === puntosPareja2.value.PV && 
         puntosPareja1.value.PV !== 0
})

const calcularPuntos = (parejaNum) => {
  const pareja = parejaNum === 1 ? puntosPareja1.value : puntosPareja2.value
  const parejaContraria = parejaNum === 1 ? puntosPareja2.value : puntosPareja1.value
  
  if (esMesaIncompleta.value) {
    const PT = Math.round(campeonatoPM.value / 2)
    pareja.PT = PT
    pareja.PV = PT
    pareja.PC = PT
    pareja.PG = 1
    pareja.MG = Math.floor(PT / 30)
    
    if (parejaContraria && tieneJugadoresActivosPareja2.value) {
      parejaContraria.PT = PT
      parejaContraria.PV = PT
      parejaContraria.PC = PT
      parejaContraria.PG = 1
      parejaContraria.MG = Math.floor(PT / 30)
    }
  } else {
    if (pareja.PT < 0) pareja.PT = 0
    if (pareja.PT > campeonatoPM.value * 2) pareja.PT = campeonatoPM.value * 2
    
    pareja.PV = Math.min(pareja.PT, campeonatoPM.value)
    parejaContraria.PV = Math.min(parejaContraria.PT, campeonatoPM.value)
    
    pareja.PC = pareja.PV - parejaContraria.PV
    parejaContraria.PC = parejaContraria.PV - pareja.PV
    
    pareja.PG = pareja.PC > 0 ? 1 : 0
    parejaContraria.PG = parejaContraria.PC > 0 ? 1 : 0
  }
}

const asignarPuntosAutomaticos = () => {
  const PT = Math.round(campeonatoPM.value / 2)
  
  const puntosAutomaticos = {
    PT: PT,
    PV: PT,
    PC: PT,
    PG: 1,
    MG: Math.floor(PT / 30)
  }
  
  if (props.mesa.pareja1?.jugador1?.activo || props.mesa.pareja1?.jugador2?.activo) {
    puntosPareja1.value = { ...puntosAutomaticos }
  }
  
  if (tieneJugadoresActivosPareja2.value) {
    puntosPareja2.value = { ...puntosAutomaticos }
  }
}

const cargarResultadoExistente = () => {
  console.log('Cargando resultado existente:', props.resultadoExistente)
  
  if (!props.resultadoExistente || !Array.isArray(props.resultadoExistente)) {
    console.log('No hay resultado existente o no es un array')
    return
  }

  try {
    // Filtrar resultados por pareja
    const resultadosPareja1 = props.resultadoExistente.filter(r => r.pareja === 1)
    const resultadosPareja2 = props.resultadoExistente.filter(r => r.pareja === 2)

    console.log('Resultados Pareja 1:', resultadosPareja1)
    console.log('Resultados Pareja 2:', resultadosPareja2)

    if (resultadosPareja1.length > 0) {
      // Crear un nuevo objeto con todos los campos
      puntosPareja1.value = {
        PT: parseInt(resultadosPareja1[0].PT) || 0,
        MG: parseInt(resultadosPareja1[0].MG) || 0,
        PV: parseInt(resultadosPareja1[0].PV) || 0,
        PG: parseInt(resultadosPareja1[0].PG) || 0,
        PC: parseInt(resultadosPareja1[0].PC) || 0
      }
    }

    if (resultadosPareja2.length > 0) {
      // Crear un nuevo objeto con todos los campos
      puntosPareja2.value = {
        PT: parseInt(resultadosPareja2[0].PT) || 0,
        MG: parseInt(resultadosPareja2[0].MG) || 0,
        PV: parseInt(resultadosPareja2[0].PV) || 0,
        PG: parseInt(resultadosPareja2[0].PG) || 0,
        PC: parseInt(resultadosPareja2[0].PC) || 0
      }
    }

    console.log('Puntos cargados:', {
      puntosPareja1: puntosPareja1.value,
      puntosPareja2: puntosPareja2.value
    })
  } catch (error) {
    console.error('Error al procesar resultados:', error)
  }
}

const obtenerPM = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/campeonatos/${props.campeonatoId}`)
    if (response.ok) {
      const campeonato = await response.json()
      campeonatoPM.value = campeonato.PM
    }
  } catch (error) {
    console.error('Error al obtener PM del campeonato:', error)
  }
}

const guardarResultados = async () => {
  try {
    const datos = {
      campeonato_id: parseInt(props.campeonatoId),
      partida: parseInt(props.partidaActual),
      mesa: parseInt(props.mesa.numeroMesa),
      es_ultima_mesa: props.esUltimaMesa || esMesaIncompleta.value,
      jugador1_id: props.mesa.pareja1?.jugador1_id || null,
      jugador2_id: props.mesa.pareja1?.jugador2_id || null,
      jugador3_id: props.mesa.pareja2?.jugador1_id || null,
      jugador4_id: props.mesa.pareja2?.jugador2_id || null,
      puntos_pareja1: parseInt(puntosPareja1.value.PT) || 0,
      puntos_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.PT) || 0 : null,
      manos_ganadas_pareja1: parseInt(puntosPareja1.value.MG) || 0,
      manos_ganadas_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.MG) || 0 : null
    }

    const method = props.resultadoExistente ? 'PUT' : 'POST'
    
    const response = await fetch('http://localhost:8000/api/resultados/mesa/', {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      body: JSON.stringify(datos)
    })

    if (!response.ok) {
      const responseData = await response.json()
      throw new Error(responseData.detail || 'Error al guardar los resultados')
    }

    emit('resultadoRegistrado', { mesa: datos.mesa, registrado: true })
    emit('close')

  } catch (error) {
    console.error('Error al guardar resultados:', error)
    alert('Error al guardar los resultados: ' + error.message)
  }
}

const validarPuntos = () => {
  if (esMesaIncompleta.value) return true

  if (puntosPareja1.value.PT < 0 || puntosPareja1.value.PT > campeonatoPM.value * 2 ||
      (props.mesa.pareja2?.jugador1 && (puntosPareja2.value.PT < 0 || puntosPareja2.value.PT > campeonatoPM.value * 2))) {
    alert('Los puntos totales deben estar entre 0 y ' + (campeonatoPM.value * 2))
    return false
  }

  if (puntosPareja1.value.MG < 0 || puntosPareja1.value.MG > 20 ||
      (props.mesa.pareja2?.jugador1 && (puntosPareja2.value.MG < 0 || puntosPareja2.value.MG > 20))) {
    alert('Las manos ganadas deben estar entre 0 y 20')
    return false
  }

  const mesaCompleta = props.mesa.pareja1?.jugador1?.activo && 
                      props.mesa.pareja1?.jugador2?.activo && 
                      props.mesa.pareja2?.jugador1?.activo && 
                      props.mesa.pareja2?.jugador2?.activo
  
  if (mesaCompleta && puntosPareja1.value.PV === puntosPareja2.value.PV && 
      puntosPareja1.value.PV !== 0) {
    alert('Los PV no pueden ser iguales en una mesa completa')
    return false
  }

  return true
}

watch(() => props.campeonatoId, obtenerPM, { immediate: true })

watch(() => props.resultadoExistente, (newVal) => {
  if (newVal) {
    nextTick(() => {
      cargarResultadoExistente()
    })
  }
}, { immediate: true })

watch(() => props.show, async (newVal) => {
  if (!newVal) {
    limpiarCampos()
    return
  }

  await obtenerPM()
  
  if (props.resultadoExistente) {
    await nextTick()
    cargarResultadoExistente()
  } else if (esMesaIncompleta.value) {
    asignarPuntosAutomaticos()
  }

  nextTick(() => {
    const inputs = document.querySelectorAll('.pareja-resultados input')
    inputs.forEach(input => {
      const isDisabled = esMesaIncompleta.value || 
                        input.id.includes('pv-') || 
                        input.id.includes('pg-') || 
                        input.id.includes('pc-')
      input.disabled = isDisabled
    })
  })
}, { immediate: true })
</script>

<style scoped>
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
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 1000px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.resultados-container {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  margin: 2rem 0;
}

.pareja-resultados {
  flex: 1;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.pareja-info {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.jugador {
  font-size: 1.1em;
  margin: 0.5rem 0;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  width: 100%;
}

.jugador-separator {
  font-size: 1.1em;
  margin: 0.25rem 0;
  color: #666;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
}

.puntos-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.input-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.input-group label {
  font-weight: bold;
  margin-bottom: 0.3rem;
  color: #666;
}

.input-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  font-size: 1.1em;
  text-align: center;
}

.input-group input:disabled {
  background-color: #f8f9fa;
  color: #333;
}

.input-group input.error {
  border-color: #dc3545;
  background-color: #fff3f3;
}

.separador {
  display: flex;
  align-items: center;
  font-weight: bold;
  color: #666;
  font-size: 1.2em;
}

.error-message {
  color: #dc3545;
  text-align: center;
  margin-top: 1rem;
  font-weight: bold;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

button {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1.1em;
}

.btn-guardar {
  background-color: #4CAF50;
  color: white;
}

.btn-guardar:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-guardar:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #cccccc;
}

.btn-cancelar {
  background-color: #f0f0f0;
  color: #666;
}

.btn-cancelar:hover {
  background-color: #e0e0e0;
}

.empty-pareja {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  background-color: #f8f9fa;
}

.no-jugadores-mensaje {
  color: #666;
  font-style: italic;
  text-align: center;
}

.mesa-incompleta-aviso {
  background-color: #fff3cd;
  color: #856404;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #ffeeba;
}

.aviso-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.aviso-header i {
  font-size: 1.2rem;
}

.mesa-incompleta-aviso ul {
  margin: 0.5rem 0 0 1.5rem;
  padding: 0;
}

.mesa-incompleta-aviso li {
  margin-bottom: 0.25rem;
}

.mesa-incompleta-aviso li:last-child {
  margin-bottom: 0;
}
</style> 