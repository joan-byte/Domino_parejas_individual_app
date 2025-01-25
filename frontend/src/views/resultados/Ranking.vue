<template>
  <div class="ranking">
    <div class="header">
      <h2>Ranking</h2>
      <div class="partida-info" v-if="campeonatoSeleccionado">
        <span>Partida: {{ partidaActual }}</span>
      </div>
    </div>

    <table class="ranking-table" v-if="jugadoresRanking.length > 0">
      <thead>
        <tr>
          <th>Ranking</th>
          <th>Partida</th>
          <th>PG</th>
          <th>PC</th>
          <th>PT</th>
          <th>ID</th>
          <th>Nombre</th>
          <th>Apellidos</th>
          <th>Club</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(jugador, index) in jugadoresRanking" :key="jugador.id">
          <td>{{ index + 1 }}</td>
          <td :class="{ 'partida-anterior': jugador.ultima_partida < partidaActual }">
            {{ jugador.ultima_partida || '-' }}
          </td>
          <td>{{ jugador.PG }}</td>
          <td>{{ jugador.PC }}</td>
          <td>{{ jugador.PT }}</td>
          <td>{{ jugador.id }}</td>
          <td>{{ jugador.nombre }}</td>
          <td>{{ jugador.apellidos }}</td>
          <td>{{ jugador.club }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const parejas = ref([])
const resultados = ref([])
const partidaActual = ref(1)
const campeonatoSeleccionado = ref(null)
const rankingData = ref([])

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
  }
}

const jugadoresRanking = computed(() => {
  return rankingData.value.map((jugador, index) => ({
    posicion: index + 1,
    id: jugador.jugador_id,
    nombre: jugador.nombre,
    apellidos: jugador.apellidos,
    club: jugador.club,
    PG: jugador.PG,
    PC: jugador.PC,
    PT: jugador.PT,
    ultima_partida: jugador.ultima_partida
  }))
})

const actualizarDatos = async () => {
  if (!campeonatoSeleccionado.value) return

  try {
    const response = await fetch(`http://localhost:8000/api/v1/ranking/campeonato/${campeonatoSeleccionado.value.id}`)
    if (response.ok) {
      const ranking = await response.json()
      rankingData.value = ranking
    }
  } catch (error) {
    console.error('Error al actualizar datos:', error)
  }
}

// Escuchar el evento de actualización del ranking
const handleRankingUpdate = () => {
  actualizarDatos()
}

onMounted(() => {
  checkCampeonatoSeleccionado()
  window.addEventListener('storage', checkCampeonatoSeleccionado)
  window.addEventListener('ranking-update', handleRankingUpdate)
  
  // Cargar datos iniciales
  actualizarDatos()
})

onUnmounted(() => {
  window.removeEventListener('storage', checkCampeonatoSeleccionado)
  window.removeEventListener('ranking-update', handleRankingUpdate)
})
</script>

<style scoped>
.ranking {
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

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ranking-table th,
.ranking-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.ranking-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #2c3e50;
}

.ranking-table tr:hover {
  background-color: #f8f9fa;
}

.partida-anterior {
  color: red;
  font-weight: bold;
}

/* Centrar columnas numéricas */
.ranking-table td:nth-child(1),
.ranking-table td:nth-child(2),
.ranking-table td:nth-child(3),
.ranking-table td:nth-child(4),
.ranking-table td:nth-child(5),
.ranking-table td:nth-child(6),
.ranking-table th:nth-child(1),
.ranking-table th:nth-child(2),
.ranking-table th:nth-child(3),
.ranking-table th:nth-child(4),
.ranking-table th:nth-child(5),
.ranking-table th:nth-child(6) {
  text-align: center;
}
</style> 