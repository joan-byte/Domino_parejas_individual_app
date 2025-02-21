<template>
  <div class="podium-container">
    <h1 class="title">Podium Final</h1>
    <h2 class="subtitle">Campeonato de Dominó</h2>
    <h3 class="tournament-name">{{ tournamentName }}</h3>

    <div class="podium-display">
      <!-- Segundo Lugar -->
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

      <!-- Primer Lugar -->
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

      <!-- Tercer Lugar -->
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

    <!-- Updated Ranking Table -->
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
          <tr v-for="(player, index) in currentPagePlayers" 
              :key="index"
              :class="{
                'gold-row': calculatePosition(index) === 1,
                'silver-row': calculatePosition(index) === 2,
                'bronze-row': calculatePosition(index) === 3
              }">
            <td>{{ calculatePosition(index) }} {{ getMedalEmoji(calculatePosition(index) - 1) }}</td>
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
      <div class="pagination-info">
        Mostrando jugadores {{ startIndex + 1 }} - {{ Math.min(startIndex + 10, ranking.length) }} de {{ ranking.length }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useEventBus } from '@vueuse/core'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = parseInt(route.params.campeonatoId)
const tournamentName = ref('')
const ranking = ref([])
const firstPlace = ref(null)
const secondPlace = ref(null)
const thirdPlace = ref(null)

// Paginación
const startIndex = ref(0)
const PLAYERS_PER_PAGE = 10
const ROTATION_INTERVAL = 10000 // 10 segundos
let rotationTimer = null

// Jugadores de la página actual
const currentPagePlayers = computed(() => {
  return ranking.value.slice(startIndex.value, startIndex.value + PLAYERS_PER_PAGE)
})

// Calcular la posición real del jugador
const calculatePosition = (index) => {
  return startIndex.value + index + 1
}

// Función para rotar a la siguiente página
const rotateToNextPage = () => {
  startIndex.value += PLAYERS_PER_PAGE
  if (startIndex.value >= ranking.value.length) {
    startIndex.value = 0 // Volver al inicio
  }
}

// Crear el bus de eventos para actualizar el ranking
const rankingBus = useEventBus('update-ranking')

const loadRanking = async () => {
  try {
    // Obtener la información del campeonato
    const campeonatoResponse = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!campeonatoResponse.ok) {
      throw new Error(`Error al obtener el campeonato: ${campeonatoResponse.status}`)
    }
    const campeonato = await campeonatoResponse.json()
    tournamentName.value = campeonato.nombre
    
    // Obtener el ranking final del campeonato
    const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
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
      secondPlace.value = ranking.value[1] || null
      thirdPlace.value = ranking.value[2] || null
    }

    // Reiniciar la paginación
    startIndex.value = 0
  } catch (error) {
    console.error('Error al cargar los datos:', error.message)
  }
}

// Iniciar la rotación automática
const startRotation = () => {
  stopRotation() // Asegurarse de que no haya un timer existente
  rotationTimer = setInterval(rotateToNextPage, ROTATION_INTERVAL)
}

// Detener la rotación
const stopRotation = () => {
  if (rotationTimer) {
    clearInterval(rotationTimer)
    rotationTimer = null
  }
}

// Escuchar el evento de actualización
rankingBus.on(() => {
  loadRanking()
})

onMounted(() => {
  loadRanking()
  startRotation()
})

onUnmounted(() => {
  stopRotation()
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
  font-size: 2.5em;
  margin-bottom: 0.5em;
  color: #2c3e50;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 0.5em;
  font-size: 1.5em;
}

.tournament-name {
  text-align: center;
  color: #333;
  margin-bottom: 2em;
  font-size: 1.8em;
  font-weight: bold;
}

.podium-display {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 20px;
  margin-bottom: 3em;
  min-height: 400px;
  position: relative;
}

.podium-position {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 280px;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.podium-position:hover {
  transform: translateY(-5px);
}

/* Estilos específicos para cada posición */
.gold {
  height: 400px;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%);
  z-index: 3;
}

.silver {
  height: 350px;
  background: linear-gradient(135deg, #C0C0C0 0%, #E8E8E8 100%);
  z-index: 2;
}

.bronze {
  height: 300px;
  background: linear-gradient(135deg, #cd7f32 0%, #FFE4D6 100%);
  z-index: 1;
}

.position-card {
  width: 100%;
  padding: 20px;
  text-align: center;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.player-name {
  font-size: 1.4em;
  font-weight: bold;
  margin-bottom: 15px;
  color: #2c3e50;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-row {
  display: flex;
  justify-content: space-around;
  font-size: 1.2em;
}

.medal, .trophy {
  font-size: 3em;
  margin-bottom: 15px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.ranking-table {
  margin-top: 40px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ranking-table h3 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.8em;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #2c3e50;
}

tr:hover:not(.gold-row):not(.silver-row):not(.bronze-row) {
  background-color: #f5f5f5;
}

td:first-child {
  font-weight: bold;
  color: #2c3e50;
}

.pagination-info {
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1em;
  color: #666;
}

/* Añadir transiciones suaves */
.ranking-table tbody tr {
  transition: all 0.3s ease;
}

/* Animación de fade para las filas */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.ranking-table tbody tr {
  animation: fadeIn 0.5s ease forwards;
}

/* Estilos para las filas del ranking según posición */
.gold-row {
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 237, 74, 0.2) 100%);
}

.silver-row {
  background: linear-gradient(90deg, rgba(192, 192, 192, 0.2) 0%, rgba(232, 232, 232, 0.2) 100%);
}

.bronze-row {
  background: linear-gradient(90deg, rgba(205, 127, 50, 0.2) 0%, rgba(255, 228, 214, 0.2) 100%);
}

.gold-row:hover {
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.3) 0%, rgba(255, 237, 74, 0.3) 100%);
}

.silver-row:hover {
  background: linear-gradient(90deg, rgba(192, 192, 192, 0.3) 0%, rgba(232, 232, 232, 0.3) 100%);
}

.bronze-row:hover {
  background: linear-gradient(90deg, rgba(205, 127, 50, 0.3) 0%, rgba(255, 228, 214, 0.3) 100%);
}
</style> 