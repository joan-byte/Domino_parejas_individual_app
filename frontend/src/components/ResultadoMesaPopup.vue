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

      <div class="error-message" v-if="pvIguales && !esUltimaMesaIncompleta">
        Los PV no pueden ser iguales
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
    type: Object,
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
const campeonatoPM = ref(300) // Valor por defecto

const calcularPuntos = (parejaNum) => {
  const pareja = parejaNum === 1 ? puntosPareja1.value : puntosPareja2.value
  const parejaContraria = parejaNum === 1 ? puntosPareja2.value : puntosPareja1.value
  
  // Validar PT (máximo el doble del PM)
  if (pareja.PT < 0) pareja.PT = 0
  if (pareja.PT > campeonatoPM.value * 2) pareja.PT = campeonatoPM.value * 2
  
  // Calcular PV usando el PM del campeonato
  pareja.PV = Math.min(pareja.PT, campeonatoPM.value)
  
  // Calcular PC (diferencia entre PV)
  pareja.PC = pareja.PV - parejaContraria.PV
  parejaContraria.PC = parejaContraria.PV - pareja.PV
  
  // Calcular PG
  pareja.PG = pareja.PC > 0 ? 1 : 0
  parejaContraria.PG = parejaContraria.PC > 0 ? 1 : 0
}

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

// Obtener el PM del campeonato al montar el componente
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

// Llamar a obtenerPM cuando el componente se monta y cuando cambia el campeonatoId
watch(() => props.campeonatoId, obtenerPM, { immediate: true })

watch(() => props.resultadoExistente, (newVal) => {
  if (newVal) {
    puntosPareja1.value.PT = newVal.puntos_pareja1
    puntosPareja1.value.MG = newVal.manos_ganadas_pareja1
    puntosPareja2.value.PT = newVal.puntos_pareja2
    puntosPareja2.value.MG = newVal.manos_ganadas_pareja2
    calcularPuntos(1)
    calcularPuntos(2)
  }
}, { immediate: true })

const pvIguales = computed(() => {
  // Solo validar PV iguales si la mesa está completa (tiene 4 jugadores)
  const mesaCompleta = props.mesa.pareja1?.jugador1 && props.mesa.pareja1?.jugador2 && 
                      props.mesa.pareja2?.jugador1 && props.mesa.pareja2?.jugador2;
  return mesaCompleta && 
         puntosPareja1.value.PV === puntosPareja2.value.PV && 
         puntosPareja1.value.PV !== 0;
})

const validarPuntos = () => {
  // Validar que los puntos totales estén dentro del rango (0 a 2*PM)
  if (puntosPareja1.value.PT < 0 || puntosPareja1.value.PT > campeonatoPM.value * 2 ||
      (props.mesa.pareja2?.jugador1 && (puntosPareja2.value.PT < 0 || puntosPareja2.value.PT > campeonatoPM.value * 2))) {
    alert('Los puntos totales deben estar entre 0 y ' + (campeonatoPM.value * 2))
    return false
  }

  // Validar que las manos ganadas estén dentro del rango (0-20)
  if (puntosPareja1.value.MG < 0 || puntosPareja1.value.MG > 20 ||
      (props.mesa.pareja2?.jugador1 && (puntosPareja2.value.MG < 0 || puntosPareja2.value.MG > 20))) {
    alert('Las manos ganadas deben estar entre 0 y 20')
    return false
  }

  // Solo validar PV iguales si la mesa está completa (tiene 4 jugadores)
  const mesaCompleta = props.mesa.pareja1?.jugador1 && props.mesa.pareja1?.jugador2 && 
                      props.mesa.pareja2?.jugador1 && props.mesa.pareja2?.jugador2;
  
  if (mesaCompleta && puntosPareja1.value.PV === puntosPareja2.value.PV && 
      puntosPareja1.value.PV !== 0) {
    alert('Los PV no pueden ser iguales en una mesa completa')
    return false
  }

  return true
}

// Modificar el computed property para detectar si es una mesa incompleta
const esMesaIncompleta = computed(() => {
  if (!props.mesa) return false
  
  // Verificar si falta algún jugador o está inactivo
  const jugadoresInactivos = [
    !props.mesa.pareja1?.jugador1?.activo,
    !props.mesa.pareja1?.jugador2?.activo,
    !props.mesa.pareja2?.jugador1?.activo,
    !props.mesa.pareja2?.jugador2?.activo
  ]

  // Si algún jugador está inactivo o falta (undefined/null), la mesa es incompleta
  return jugadoresInactivos.some(inactivo => inactivo === true || inactivo === undefined)
})

// Añadir computed property para obtener los jugadores activos
const jugadoresActivos = computed(() => {
  const jugadores = []
  
  // Jugadores de la pareja 1
  if (props.mesa.pareja1?.jugador1) {
    jugadores.push({
      id: props.mesa.pareja1.jugador1_id,
      numero: 1,
      pareja: 1
    })
  }
  if (props.mesa.pareja1?.jugador2) {
    jugadores.push({
      id: props.mesa.pareja1.jugador2_id,
      numero: 2,
      pareja: 1
    })
  }
  
  // Jugadores de la pareja 2
  if (props.mesa.pareja2?.jugador1) {
    jugadores.push({
      id: props.mesa.pareja2.jugador1_id,
      numero: 3,
      pareja: 2
    })
  }
  if (props.mesa.pareja2?.jugador2) {
    jugadores.push({
      id: props.mesa.pareja2.jugador2_id,
      numero: 4,
      pareja: 2
    })
  }
  
  return jugadores
})

const guardarResultados = async () => {
  try {
    // Preparar los datos para enviar
    const datos = {
      campeonato_id: parseInt(props.campeonatoId),
      partida: parseInt(props.partidaActual),
      mesa: parseInt(props.mesa.numeroMesa),
      es_ultima_mesa: props.esUltimaMesa || esMesaIncompleta.value,
      // Jugadores de la primera pareja
      jugador1_id: props.mesa.pareja1?.jugador1_id || null,
      jugador2_id: props.mesa.pareja1?.jugador2_id || null,
      // Jugadores de la segunda pareja
      jugador3_id: props.mesa.pareja2?.jugador1_id || null,
      jugador4_id: props.mesa.pareja2?.jugador2_id || null,
      // Puntos por pareja
      puntos_pareja1: parseInt(puntosPareja1.value.PT) || 0,
      puntos_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.PT) || 0 : null,
      // Manos ganadas
      manos_ganadas_pareja1: parseInt(puntosPareja1.value.MG) || 0,
      manos_ganadas_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.MG) || 0 : null
    }

    console.log('Guardando resultados para mesa incompleta:', {
      esMesaIncompleta: esMesaIncompleta.value,
      jugadoresActivos: jugadoresActivos.value,
      datos
    })

    // Determinar si es una modificación o un nuevo registro
    const method = props.resultadoExistente ? 'PUT' : 'POST'
    console.log(`Usando método ${method} para ${props.resultadoExistente ? 'modificar' : 'crear'} resultados`)

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
      console.error('Error response:', responseData)
      throw new Error(responseData.detail || 'Error al guardar los resultados')
    }

    const responseData = await response.json()
    console.log('Respuesta del servidor:', responseData)
    
    // Emitir eventos para actualizar la vista principal
    emit('resultadoRegistrado', { mesa: datos.mesa, registrado: true })
    emit('close')

  } catch (error) {
    console.error('Error al guardar resultados:', error)
    alert('Error al guardar los resultados: ' + error.message)
  }
}

const limpiarCampos = () => {
  puntosPareja1.value = { PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 }
  puntosPareja2.value = { PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 }
}

const cerrar = () => {
  limpiarCampos()
  emit('close')
}

// Añadir computed property para detectar si es una mesa incompleta
const esUltimaMesaIncompleta = computed(() => {
  return props.esUltimaMesa && (
    !props.mesa.pareja2?.jugador1 || 
    !props.mesa.pareja1?.jugador2 ||
    !props.mesa.pareja2?.jugador2
  )
})

const puntosAutomaticos = computed(() => {
  if (!esMesaIncompleta.value || !campeonatoPM.value) return null
  
  const PT = Math.round(campeonatoPM.value / 2)
  return {
    PT: PT,
    PV: PT,
    PC: PT,
    PG: 1,
    MG: Math.floor(PT / 30)
  }
})

// Modificar el watch del show para añadir logs
watch(() => props.show, async (newVal) => {
  console.log('Watch show activado:', {
    newVal,
    mesa: props.mesa,
    campeonatoId: props.campeonatoId,
    partidaActual: props.partidaActual,
    resultadoExistente: props.resultadoExistente
  })
  
  if (!newVal) {
    limpiarCampos()
    return
  }

  // Asegurarse de que tenemos el PM del campeonato antes de continuar
  await obtenerPM()
  
  // Si hay un resultado existente, cargarlo
  if (props.resultadoExistente) {
    console.log('Cargando resultado existente:', props.resultadoExistente)
    puntosPareja1.value = {
      PT: props.resultadoExistente.puntos_pareja1,
      MG: props.resultadoExistente.manos_ganadas_pareja1,
      PV: Math.min(props.resultadoExistente.puntos_pareja1, campeonatoPM.value),
      PG: props.resultadoExistente.puntos_pareja1 > 0 ? 1 : 0,
      PC: props.resultadoExistente.puntos_pareja1
    }
    
    if (props.resultadoExistente.puntos_pareja2 !== null) {
      puntosPareja2.value = {
        PT: props.resultadoExistente.puntos_pareja2,
        MG: props.resultadoExistente.manos_ganadas_pareja2,
        PV: Math.min(props.resultadoExistente.puntos_pareja2, campeonatoPM.value),
        PG: props.resultadoExistente.puntos_pareja2 > 0 ? 1 : 0,
        PC: props.resultadoExistente.puntos_pareja2
      }
    }
    calcularPuntos(1)
    calcularPuntos(2)
  } 
  // Si la mesa está incompleta y no hay resultado existente
  else if (esMesaIncompleta.value) {
    console.log('Mesa incompleta detectada, asignando puntos automáticos')
    
    const puntosAuto = puntosAutomaticos.value
    if (!puntosAuto) {
      console.error('No se pudieron calcular los puntos automáticos')
      return
    }
    
    console.log('Puntos automáticos calculados:', puntosAuto)
    
    // Asignar puntos automáticos a las parejas con jugadores activos
    if (props.mesa.pareja1?.jugador1?.activo || props.mesa.pareja1?.jugador2?.activo) {
      Object.assign(puntosPareja1.value, puntosAuto)
      console.log('Puntos asignados a pareja 1:', puntosPareja1.value)
    }
    
    if (props.mesa.pareja2?.jugador1?.activo || props.mesa.pareja2?.jugador2?.activo) {
      Object.assign(puntosPareja2.value, puntosAuto)
      console.log('Puntos asignados a pareja 2:', puntosPareja2.value)
    }
  }

  // Actualizar estado de los inputs
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

// Añadir computed property para verificar si hay jugadores activos en la pareja 2
const tieneJugadoresActivosPareja2 = computed(() => {
  return props.mesa.pareja2?.jugador1?.activo || props.mesa.pareja2?.jugador2?.activo
})
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