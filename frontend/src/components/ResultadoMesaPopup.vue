<template>
  <div class="popup-overlay" v-if="show">
    <div class="popup-content">
      <h3>Registro de Resultados - Mesa {{ mesa.numeroMesa }}</h3>
      
      <div class="resultados-container">
        <div class="pareja-resultados">
          <div class="pareja-info">
            <div class="jugador">
              {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}
            </div>
            <div class="jugador">
              {{ mesa.pareja1.jugador2_id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
            </div>
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
                max="600"
                @input="calcularPuntos(1)"
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
              <label for="pc-pareja1">PC:</label>
              <input 
                id="pc-pareja1"
                name="pc-pareja1"
                type="number" 
                :value="puntosPareja1.PC" 
                disabled
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
          </div>
        </div>

        <div class="separador">VS</div>

        <div class="pareja-resultados">
          <div class="pareja-info">
            <div class="jugador">
              {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}
            </div>
            <div class="jugador">
              {{ mesa.pareja2.jugador2_id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
            </div>
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
                max="600"
                @input="calcularPuntos(2)"
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
              <label for="pc-pareja2">PC:</label>
              <input 
                id="pc-pareja2"
                name="pc-pareja2"
                type="number" 
                :value="puntosPareja2.PC" 
                disabled
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
          </div>
        </div>
      </div>

      <div class="error-message" v-if="pvIguales">
        Los PV no pueden ser iguales
      </div>

      <div class="actions">
        <button 
          @click="guardarResultados" 
          class="btn-guardar"
          :disabled="pvIguales"
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

const props = defineProps({
  show: Boolean,
  mesa: Object,
  campeonatoId: Number,
  partida: Number,
  resultadoExistente: Object
})

const emit = defineEmits(['update:show', 'resultadoGuardado'])

const puntosPareja1 = ref({ PT: 0, PV: 0, PC: 0, PG: 0 })
const puntosPareja2 = ref({ PT: 0, PV: 0, PC: 0, PG: 0 })

const pvIguales = computed(() => {
  return puntosPareja1.value.PV === puntosPareja2.value.PV && 
         puntosPareja1.value.PV !== 0
})

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
  
  // Validar PT
  if (pareja.PT < 0) pareja.PT = 0
  if (pareja.PT > 600) pareja.PT = 600
  
  // Calcular PV (máximo 300)
  pareja.PV = Math.min(pareja.PT, 300)
  
  // Calcular PC (diferencia entre PV)
  pareja.PC = pareja.PV - parejaContraria.PV
  parejaContraria.PC = parejaContraria.PV - pareja.PV
  
  // Calcular PG
  pareja.PG = pareja.PC > 0 ? 1 : 0
  parejaContraria.PG = parejaContraria.PC > 0 ? 1 : 0
}

const guardarResultados = async () => {
  if (pvIguales.value) return

  const datos = {
    campeonato_id: props.campeonatoId,
    partida: props.partida,
    mesa: props.mesa.numeroMesa,
    jugador1_id: props.mesa.pareja1.jugador1_id,
    jugador2_id: props.mesa.pareja1.jugador2_id,
    jugador3_id: props.mesa.pareja2.jugador1_id,
    jugador4_id: props.mesa.pareja2.jugador2_id,
    puntos_pareja1: puntosPareja1.value.PT,
    puntos_pareja2: puntosPareja2.value.PT
  }

  try {
    const url = 'http://localhost:8000/api/v1/resultados/mesa/'
    const method = props.resultadoExistente ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos)
    })
    
    if (response.ok) {
      await onResultadoGuardado()
    } else {
      console.error('Error al guardar resultados')
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const onResultadoGuardado = async () => {
  try {
    // Esperar un momento para asegurar que los datos se han guardado
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Disparar evento para actualizar el ranking
    window.dispatchEvent(new Event('ranking-update'))
    
    // Cerrar el popup
    emit('close')
  } catch (error) {
    console.error('Error al procesar el guardado:', error)
  }
}

const limpiarCampos = () => {
  puntosPareja1.value = { PT: 0, PV: 0, PC: 0, PG: 0 }
  puntosPareja2.value = { PT: 0, PV: 0, PC: 0, PG: 0 }
}

const cerrar = () => {
  limpiarCampos()
  emit('update:show', false)
}

// Limpiar campos cuando se cierra el popup
watch(() => props.show, (newVal) => {
  if (!newVal) {
    limpiarCampos()
  } else {
    // Cuando se abre el popup, enfocamos el campo PT de la pareja 1
    setTimeout(() => {
      document.getElementById('pt-pareja1')?.focus()
    }, 100)
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
}

.jugador {
  font-size: 1.1em;
  margin: 0.5rem 0;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
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
</style> 