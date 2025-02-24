<template>
  <div class="popup-overlay" v-if="show">
    <div class="popup-content">
      <h3>Registro de Resultados - Mesa {{ mesa.numeroMesa }}</h3>
      
      <div class="resultados-container">
        <div class="pareja-resultados">
          <div class="pareja-info">
            <div class="jugador" v-if="mesa.pareja1?.jugador1">
              {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
            </div>
            <template v-if="mesa.pareja1?.jugador2">
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
                v-model="puntosPareja1.PT" 
                min="0" 
                :max="campeonatoPM * 2"
                @input="calcularPuntos(1)"
              >
            </div>
            <div class="input-group">
              <label for="mg-pareja1">MG:</label>
              <input 
                id="mg-pareja1"
                name="mg-pareja1"
                type="number" 
                v-model="puntosPareja1.MG" 
                min="0"
                max="20"
              >
            </div>
            <div class="input-group">
              <label for="pv-pareja1">PV:</label>
              <input 
                id="pv-pareja1"
                name="pv-pareja1"
                type="number" 
                :value="puntosPareja1.PV" 
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
                :value="puntosPareja1.PG" 
                disabled
              >
            </div>
            <div class="input-group">
              <label for="pc-pareja1">Dif.:</label>
              <input 
                id="pc-pareja1"
                name="pc-pareja1"
                type="number" 
                :value="puntosPareja1.PC" 
                disabled
              >
            </div>
          </div>
        </div>

        <div class="separador">VS</div>

        <div class="pareja-resultados" v-if="mesa.pareja2?.jugador1">
          <div class="pareja-info">
            <div class="jugador">
              {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
            </div>
            <template v-if="mesa.pareja2?.jugador2">
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
                v-model="puntosPareja2.PT" 
                min="0" 
                :max="campeonatoPM * 2"
                @input="calcularPuntos(2)"
              >
            </div>
            <div class="input-group">
              <label for="mg-pareja2">MG:</label>
              <input 
                id="mg-pareja2"
                name="mg-pareja2"
                type="number" 
                v-model="puntosPareja2.MG" 
                min="0"
                max="20"
              >
            </div>
            <div class="input-group">
              <label for="pv-pareja2">PV:</label>
              <input 
                id="pv-pareja2"
                name="pv-pareja2"
                type="number" 
                :value="puntosPareja2.PV" 
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
                :value="puntosPareja2.PG" 
                disabled
              >
            </div>
            <div class="input-group">
              <label for="pc-pareja2">Dif.:</label>
              <input 
                id="pc-pareja2"
                name="pc-pareja2"
                type="number" 
                :value="puntosPareja2.PC" 
                disabled
              >
            </div>
          </div>
        </div>
        <div class="pareja-resultados empty-pareja" v-else>
          <div class="no-jugadores-mensaje">
            No hay jugadores en la segunda pareja
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
          :disabled="pvIguales && !esUltimaMesaIncompleta"
        >
          Guardar
        </button>
        <button @click="cerrar" class="btn-cancelar">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useEventBus } from '@vueuse/core'

const props = defineProps({
  show: Boolean,
  mesa: Object,
  campeonatoId: Number,
  partidaActual: {
    type: Number,
    required: true
  },
  resultadoExistente: Object,
  esUltimaMesa: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'resultadoRegistrado'])

const puntosPareja1 = ref({ PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 })
const puntosPareja2 = ref({ PT: 0, PV: 0, PC: 0, PG: 0, MG: 0 })
const campeonatoPM = ref(300) // Valor por defecto

const pvIguales = computed(() => {
  // Solo validar PV iguales si la mesa está completa (tiene 4 jugadores)
  const mesaCompleta = props.mesa.pareja1?.jugador1 && props.mesa.pareja1?.jugador2 && 
                      props.mesa.pareja2?.jugador1 && props.mesa.pareja2?.jugador2;
  return mesaCompleta && 
         puntosPareja1.value.PV === puntosPareja2.value.PV && 
         puntosPareja1.value.PV !== 0;
})

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
    puntosPareja2.value.PT = newVal.puntos_pareja2
    calcularPuntos(1)
    calcularPuntos(2)
  }
}, { immediate: true })

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

const guardarResultados = async () => {
  if (!validarPuntos()) {
    alert('Por favor, verifica los puntos ingresados.')
    return
  }

  try {
    // Log de los props recibidos
    console.log('Props recibidos:', {
      campeonatoId: props.campeonatoId,
      partidaActual: props.partidaActual,
      mesa: props.mesa?.numeroMesa
    })

    // Asegurarnos de que todos los valores son números enteros
    const datos = {
      campeonato_id: parseInt(props.campeonatoId),
      partida: parseInt(props.partidaActual),
      mesa: parseInt(props.mesa.numeroMesa),
      es_ultima_mesa: props.esUltimaMesa,
      jugador1_id: parseInt(props.mesa.pareja1.jugador1_id),
      jugador2_id: parseInt(props.mesa.pareja1.jugador2_id),
      jugador3_id: props.mesa.pareja2?.jugador1_id ? parseInt(props.mesa.pareja2.jugador1_id) : null,
      jugador4_id: props.mesa.pareja2?.jugador2_id ? parseInt(props.mesa.pareja2.jugador2_id) : null,
      puntos_pareja1: parseInt(puntosPareja1.value.PT) || 0,
      puntos_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.PT) || 0 : null,
      mesas_ganadas_pareja1: parseInt(puntosPareja1.value.MG) || 0,
      mesas_ganadas_pareja2: props.mesa.pareja2?.jugador1_id ? parseInt(puntosPareja2.value.MG) || 0 : null
    }

    // Log de los datos antes de la validación
    console.log('Datos antes de validación:', {
      ...datos,
      props: {
        campeonatoId: props.campeonatoId,
        partidaActual: props.partidaActual,
        mesa: props.mesa
      }
    })

    // Validar que todos los campos requeridos estén presentes y sean números
    const camposRequeridos = [
      'campeonato_id', 'partida', 'mesa', 
      'jugador1_id'
    ]

    // Si no es una mesa incompleta, agregar los campos adicionales requeridos
    if (!esUltimaMesaIncompleta.value) {
      camposRequeridos.push('jugador2_id', 'puntos_pareja1', 'mesas_ganadas_pareja1')
    }

    const camposFaltantes = camposRequeridos.filter(campo => {
      const valor = datos[campo]
      const esInvalido = valor === undefined || valor === null || isNaN(valor)
      if (esInvalido) {
        console.log(`Campo inválido ${campo}:`, valor)
      }
      return esInvalido
    })

    if (camposFaltantes.length > 0) {
      throw new Error(`Campos inválidos o faltantes: ${camposFaltantes.join(', ')}`)
    }

    console.log('Datos a enviar:', JSON.stringify(datos, null, 2))

    const response = await fetch('http://localhost:8000/api/resultados/mesa/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos)
    })

    const responseData = await response.json()
    
    if (!response.ok) {
      console.error('Error response status:', response.status)
      console.error('Error response data:', responseData)
      
      let mensajeError = 'Error al guardar los resultados'
      if (responseData.detail) {
        if (Array.isArray(responseData.detail)) {
          mensajeError = responseData.detail.join(', ')
        } else {
          mensajeError = responseData.detail
        }
      }
      
      throw new Error(mensajeError)
    }

    console.log('Resultados guardados correctamente')
    
    // Emitir el evento para actualizar el ranking
    rankingBus.emit()
    console.log('Evento de actualización de ranking emitido')
    
    // Esperar un momento antes de cerrar para asegurar que el evento se procese
    setTimeout(() => {
      emit('resultadoRegistrado')
      emit('close')
    }, 100)

  } catch (error) {
    console.error('Error completo:', error)
    console.error('Stack trace:', error.stack)
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

// Modificar el watch del show
watch(() => props.show, (newVal) => {
  if (!newVal) {
    limpiarCampos()
  } else {
    // Si es la última mesa y está incompleta
    if (esUltimaMesaIncompleta.value) {
      // Asignar la mitad del PM como PT para la pareja que tiene jugadores
      const ptAutomatico = Math.ceil(campeonatoPM.value / 2)  // Redondeo hacia arriba
      
      // Asignar puntos a la primera pareja si tiene al menos un jugador
      if (props.mesa.pareja1?.jugador1) {
        puntosPareja1.value.PT = ptAutomatico
        puntosPareja1.value.MG = Math.ceil(ptAutomatico / 30)
        puntosPareja1.value.PV = ptAutomatico
        puntosPareja1.value.PG = 1
        puntosPareja1.value.PC = ptAutomatico
      }
      
      // Si hay segunda pareja, asignar puntos también
      if (props.mesa.pareja2?.jugador1) {
        puntosPareja2.value.PT = ptAutomatico
        puntosPareja2.value.MG = Math.ceil(ptAutomatico / 30)
        puntosPareja2.value.PV = ptAutomatico
        puntosPareja2.value.PG = 1
        puntosPareja2.value.PC = ptAutomatico
      }
      
      // Deshabilitar la edición de los campos y guardar automáticamente
      setTimeout(() => {
        const inputs = document.querySelectorAll('.pareja-resultados input')
        inputs.forEach(input => {
          input.disabled = true
        })
        guardarResultados()
      }, 100)
    } else {
      // Cuando se abre el popup normalmente, enfocamos el campo PT de la pareja 1
      setTimeout(() => {
        document.getElementById('pt-pareja1')?.focus()
      }, 100)
    }
  }
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
</style> 