<template>
  <div class="registro-mesas">
    <div class="header">
      <h2>Registro de Mesas</h2>
      <div class="partida-info">
        <span>Partida: {{ partida }}</span>
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
      :partida="partida"
      :resultado-existente="resultadoExistente"
      @resultado-guardado="onResultadoGuardado"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ResultadoMesaPopup from '@/components/ResultadoMesaPopup.vue'

const route = useRoute()
const campeonatoId = parseInt(route.params.campeonatoId)
const partida = 1 // Por ahora hardcodeado a 1
const parejas = ref([])
const showPopup = ref(false)
const mesaSeleccionada = ref(null)
const resultadoExistente = ref(null)
const mesasRegistradas = ref({})

const mesasConParejas = computed(() => {
  const mesas = new Map()
  
  parejas.value.forEach(pareja => {
    if (!mesas.has(pareja.mesa)) {
      mesas.set(pareja.mesa, {
        numeroMesa: pareja.mesa,
        pareja1: null,
        pareja2: null
      })
    }
    
    const mesaActual = mesas.get(pareja.mesa)
    if (!mesaActual.pareja1) {
      mesaActual.pareja1 = pareja
    } else {
      mesaActual.pareja2 = pareja
    }
  })
  
  return Array.from(mesas.values())
})

const cargarParejas = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/parejas-partida/campeonato/${campeonatoId}/partida/${partida}`)
    if (response.ok) {
      parejas.value = await response.json()
      await verificarMesasRegistradas()
    } else {
      console.error('Error al cargar las parejas')
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const verificarMesasRegistradas = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/resultados/campeonato/${campeonatoId}/partida/${partida}`)
    if (response.ok) {
      const resultados = await response.json()
      const mesasReg = {}
      // Agrupamos por mesa y nos aseguramos de usar el número de mesa como clave
      resultados.forEach(resultado => {
        if (resultado && resultado.mesa) {
          mesasReg[resultado.mesa] = true
        }
      })
      console.log('Mesas registradas:', mesasReg, 'Mesas con parejas:', mesasConParejas.value) // Para depuración
      mesasRegistradas.value = mesasReg
    } else if (response.status === 404) {
      mesasRegistradas.value = {}
    } else {
      console.error('Error al verificar mesas registradas')
    }
  } catch (error) {
    console.error('Error al verificar mesas registradas:', error)
    mesasRegistradas.value = {}
  }
}

const cargarResultadoMesa = async (mesa) => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/resultados/mesa/${campeonatoId}/${partida}/${mesa.numeroMesa}`)
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

onMounted(() => {
  cargarParejas()
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

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
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