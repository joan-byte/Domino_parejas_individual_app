<template>
  <div class="asignacion-mesas">
    <div class="header">
      <h2>Asignación de Mesas</h2>
      <div class="partida-info">
        <span>Partida: 1</span>
      </div>
    </div>
    
    <div v-if="jugadoresOrdenados.length > 0">
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Mesa</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="jugador in jugadoresOrdenados" :key="jugador.id">
            <td>{{ jugador.id }}</td>
            <td>{{ jugador.nombre }}</td>
            <td>{{ jugador.apellidos }}</td>
            <td>{{ jugador.club }}</td>
            <td>{{ jugador.mesa }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No hay jugadores asignados todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])

// Procesar los jugadores y sus mesas asignadas
const jugadoresOrdenados = computed(() => {
  const jugadores = []
  parejas.value.forEach(pareja => {
    // Añadir jugador 1
    jugadores.push({
      id: pareja.jugador1_id,
      nombre: pareja.jugador1.nombre,
      apellidos: pareja.jugador1.apellidos,
      club: pareja.jugador1.club,
      mesa: pareja.mesa
    })
    // Añadir jugador 2
    jugadores.push({
      id: pareja.jugador2_id,
      nombre: pareja.jugador2.nombre,
      apellidos: pareja.jugador2.apellidos,
      club: pareja.jugador2.club,
      mesa: pareja.mesa
    })
  })
  // Ordenar por ID de jugador ascendente
  return jugadores.sort((a, b) => a.id - b.id)
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
.asignacion-mesas {
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

.jugadores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.jugadores-table th,
.jugadores-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.jugadores-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #2c3e50;
}

.jugadores-table tr:hover {
  background-color: #f8f9fa;
}
</style> 