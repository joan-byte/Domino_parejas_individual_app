<template>
  <div class="registro-mesas">
    <div class="header">
      <h2>Registro de Mesas</h2>
      <div class="partida-info">
        <span>Partida: 1</span>
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
              {{ mesa.pareja1.jugador1_id }} - {{ mesa.pareja1.jugador1.nombre }} {{ mesa.pareja1.jugador1.apellidos }}, {{ mesa.pareja1.jugador2_id }} - {{ mesa.pareja1.jugador2.nombre }} {{ mesa.pareja1.jugador2.apellidos }}
            </div>
            <div class="separator">y</div>
            <div class="pareja-info">
              <span class="pareja-label">Pareja 2:</span>
              {{ mesa.pareja2.jugador1_id }} - {{ mesa.pareja2.jugador1.nombre }} {{ mesa.pareja2.jugador1.apellidos }}, {{ mesa.pareja2.jugador2_id }} - {{ mesa.pareja2.jugador2.nombre }} {{ mesa.pareja2.jugador2.apellidos }}
            </div>
          </div>
          <div class="actions">
            <button class="btn-registrar">Registrar</button>
            <button class="btn-modificar" disabled>Modificar</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>No hay mesas asignadas todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])

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
    const response = await fetch(`http://localhost:8000/api/v1/parejas-partida/campeonato/${campeonatoId}/partida/1`)
    if (response.ok) {
      parejas.value = await response.json()
    } else {
      console.error('Error al cargar las parejas')
    }
  } catch (error) {
    console.error('Error:', error)
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
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  align-items: center;
  background-color: white;
  padding: 12px 15px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  width: calc(50% - 35px);
  margin: 0 15px;
}

.jugadores-info {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

.pareja-label {
  color: #4CAF50;
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
  margin-right: 8px;
}

.jugador {
  font-size: 1em;
  white-space: nowrap;
  font-weight: 500;
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

.btn-registrar, .btn-modificar {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-registrar {
  background-color: #4CAF50;
  color: white;
}

.btn-registrar:hover {
  background-color: #45a049;
}

.btn-modificar {
  background-color: #f0f0f0;
  color: #666;
}

.btn-modificar:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-modificar:not(:disabled):hover {
  background-color: #e0e0e0;
}
</style> 