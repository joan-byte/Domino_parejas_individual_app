<template>
  <div class="podium-container">
    <h2 class="title">🏆 Podium del Campeonato 🏆</h2>
    <p class="subtitle">Parejas Individual</p>
    <p class="tournament-name">{{ tournamentName }}</p>

    <div class="podium-display">
      <!-- Plata - Segundo lugar -->
      <div class="podium-position silver">
        <div class="medal">🥈</div>
        <div class="position-card">
          <p class="player-name">{{ secondPlace?.nombre }} {{ secondPlace?.apellidos || 'Por determinar' }}</p>
          <div class="stats">
            <div class="stat-row">
              <span>PG: {{ secondPlace?.PG || '0' }}</span>
              <span>Dif.: {{ secondPlace?.PC || '0' }}</span>
            </div>
            <div class="stat-row">
              <span>PT: {{ secondPlace?.PT || '0' }}</span>
              <span>MG: {{ secondPlace?.MG || '0' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Oro - Primer lugar -->
      <div class="podium-position gold">
        <div class="trophy">🏆</div>
        <div class="position-card">
          <p class="player-name">{{ firstPlace?.nombre }} {{ firstPlace?.apellidos || 'Por determinar' }}</p>
          <div class="stats">
            <div class="stat-row">
              <span>PG: {{ firstPlace?.PG || '0' }}</span>
              <span>Dif.: {{ firstPlace?.PC || '0' }}</span>
            </div>
            <div class="stat-row">
              <span>PT: {{ firstPlace?.PT || '0' }}</span>
              <span>MG: {{ firstPlace?.MG || '0' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bronce - Tercer lugar -->
      <div class="podium-position bronze">
        <div class="medal">🥉</div>
        <div class="position-card">
          <p class="player-name">{{ thirdPlace?.nombre }} {{ thirdPlace?.apellidos || 'Por determinar' }}</p>
          <div class="stats">
            <div class="stat-row">
              <span>PG: {{ thirdPlace?.PG || '0' }}</span>
              <span>Dif.: {{ thirdPlace?.PC || '0' }}</span>
            </div>
            <div class="stat-row">
              <span>PT: {{ thirdPlace?.PT || '0' }}</span>
              <span>MG: {{ thirdPlace?.MG || '0' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabla de Ranking -->
    <div class="ranking-table">
      <h3>Ranking Final</h3>
      <table>
        <thead>
          <tr>
            <th>POSICIÓN</th>
            <th>PG</th>
            <th>Dif.</th>
            <th>PT</th>
            <th>MG</th>
            <th>ID</th>
            <th>NOMBRE</th>
            <th>APELLIDOS</th>
            <th>CLUB</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(player, index) in ranking" :key="index">
            <td>{{ index + 1 }} {{ getMedalEmoji(index) }}</td>
            <td>{{ player.PG || 0 }}</td>
            <td>{{ player.PC || 0 }}</td>
            <td>{{ player.PT || 0 }}</td>
            <td>{{ player.MG || 0 }}</td>
            <td>{{ player.jugador_id }}</td>
            <td>{{ player.nombre }}</td>
            <td>{{ player.apellidos }}</td>
            <td>{{ player.club }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEventBus } from '@vueuse/core'

const tournamentName = ref('')
const ranking = ref([])
const firstPlace = ref(null)
const secondPlace = ref(null)
const thirdPlace = ref(null)

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

const loadRanking = async () => {
  try {
    // Obtener el campeonato activo
    const campeonatoResponse = await fetch('http://localhost:8000/api/campeonatos/')
    if (!campeonatoResponse.ok) {
      throw new Error(`Error al obtener campeonatos: ${campeonatoResponse.status}`)
    }
    const campeonatos = await campeonatoResponse.json()
    
    // Verificar que campeonatos es un array
    if (!Array.isArray(campeonatos)) {
      throw new Error('La respuesta de campeonatos no es un array')
    }
    
    const campeonatoActivo = campeonatos.find(c => c.activo)
    
    if (campeonatoActivo) {
      tournamentName.value = campeonatoActivo.nombre
      
      // Obtener la última partida con resultados
      const ultimaPartidaResponse = await fetch(`http://localhost:8000/api/parejas-partida/ultima-partida/${campeonatoActivo.id}`)
      if (!ultimaPartidaResponse.ok) {
        throw new Error('Error al obtener la última partida')
      }
      const { ultima_partida } = await ultimaPartidaResponse.json()
      
      // Si no hay partidas o la partida actual es 0, no mostrar ranking
      if (!ultima_partida) {
        ranking.value = []
        firstPlace.value = null
        secondPlace.value = null
        thirdPlace.value = null
        return
      }
      
      // Obtener el ranking usando la última partida con resultados
      const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoActivo.id}?partida=${ultima_partida}`)
      if (!rankingResponse.ok) {
        throw new Error(`Error al obtener ranking: ${rankingResponse.status}`)
      }
      const rankingData = await rankingResponse.json()
      
      // Verificar que rankingData es un array
      if (!Array.isArray(rankingData)) {
        throw new Error('La respuesta del ranking no es un array')
      }
      
      ranking.value = rankingData
      
      // Asignar los primeros lugares
      if (ranking.value.length > 0) {
        firstPlace.value = ranking.value[0]
        secondPlace.value = ranking.value[1]
        thirdPlace.value = ranking.value[2]
      }
    } else {
      console.warn('No se encontró ningún campeonato activo')
    }
  } catch (error) {
    console.error('Error al cargar los datos:', error.message)
  }
}

// Escuchar el evento de actualización
rankingBus.on(() => {
  loadRanking()
})

onMounted(() => {
  loadRanking()
})

const getMedalEmoji = (index) => {
  switch (index) {
    case 0:
      return '🏆'
    case 1:
      return '🥈'
    case 2:
      return '🥉'
    default:
      return ''
  }
}
</script>

<style scoped>
.podium-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  font-size: 2em;
  margin-bottom: 0.5em;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 0.5em;
  font-size: 1.2em;
}

.tournament-name {
  text-align: center;
  color: #333;
  margin-bottom: 2em;
  font-size: 1.5em;
  font-weight: bold;
}

.podium-display {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 0;
  margin-bottom: 3em;
  min-height: 300px;
  position: relative;
}

.podium-position {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 250px;
  margin: 0;
}

/* Estilos específicos para cada posición */
.gold {
  height: 220px;
  background: #FFFDD0;
  z-index: 3;
}

.silver {
  height: 180px;
  background: #E8E8E8;
  z-index: 2;
}

.bronze {
  height: 140px;
  background: #FFE4D6;
  z-index: 1;
}

.position-card {
  width: 100%;
  padding: 12px;
  text-align: center;
  position: relative;
  z-index: 1;
  margin: 0;
  background: transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 20px;
}

.medal, .trophy {
  font-size: 2.5em;
  margin-bottom: 0;
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%);
}

.player-name {
  font-weight: bold;
  font-size: 1.1em;
  margin: 0;
  padding-top: 10px;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
}

.stat-row {
  display: flex;
  justify-content: space-around;
  gap: 15px;
}

.stat-row span {
  font-size: 1em;
  padding: 3px 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

/* Eliminar los elementos innecesarios */
.position-card h3,
.player-id,
.pedestal {
  display: none;
}

/* Eliminar bordes y sombras innecesarias */
.position-card {
  border: none;
  box-shadow: none;
}

.ranking-table {
  margin-top: 40px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* Estilos específicos para las tres primeras posiciones */
tr:nth-child(1) {
  background-color: #FFFDD0 !important; /* Color oro */
}

tr:nth-child(2) {
  background-color: #E8E8E8 !important; /* Color plata */
}

tr:nth-child(3) {
  background-color: #FFE4D6 !important; /* Color bronce */
}

tr:hover {
  background-color: inherit; /* Mantener el color al hacer hover en las tres primeras posiciones */
}

/* Para el resto de filas, mantener el hover original */
tr:nth-child(n+4):hover {
  background-color: #f5f5f5;
}

.position-card h3 {
  font-size: 1.8em;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 15px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.gold .position-card h3 {
  color: #FFE87C;
  font-size: 2em;
}

.silver .position-card h3 {
  color: #D3D3D3;
  font-size: 1.9em;
}

.bronze .position-card h3 {
  color: #DEB887;
  font-size: 1.8em;
}

/* Eliminar los pseudo-elementos que ya no necesitamos */
.podium-position::before,
.podium-position::after,
.gold::before,
.silver::before,
.bronze::before,
.gold::after,
.silver::after,
.bronze::after {
  display: none;
}
</style> 