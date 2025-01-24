<template>
  <div class="inscripcion-container">
    <button class="btn-finalizar" @click="finalizarInscripcion">
      Finalizar Inscripción
    </button>

    <h2>Inscripción de Jugador</h2>
    <form @submit.prevent="guardarJugador" class="inscripcion-form" autocomplete="off">
      <div class="form-group">
        <label for="nombre">Nombre:</label>
        <input 
          type="text" 
          id="nombre" 
          ref="nombreInput"
          v-model="jugador.nombre" 
          required 
          class="form-control"
          autocomplete="off"
        >
      </div>

      <div class="form-group">
        <label for="apellidos">Apellidos:</label>
        <input 
          type="text" 
          id="apellidos" 
          v-model="jugador.apellidos" 
          required 
          class="form-control"
          autocomplete="off"
        >
      </div>

      <div class="form-group">
        <label for="club">Club:</label>
        <input 
          type="text" 
          id="club" 
          v-model="jugador.club" 
          class="form-control"
          autocomplete="off"
        >
      </div>

      <button type="submit" class="btn-submit">Inscribir Jugador</button>
    </form>

    <div class="jugadores-list">
      <h3>Jugadores Inscritos</h3>
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Campeonato</th>
            <th>Estado</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="j in jugadores" :key="j.id">
            <td>{{ j.id }}</td>
            <td>{{ j.nombre }}</td>
            <td>{{ j.apellidos }}</td>
            <td>{{ j.club }}</td>
            <td>{{ j.campeonato_id }}</td>
            <td :class="['estado', j.activo ? 'estado-activo' : 'estado-inactivo']">
              {{ j.activo ? 'Activo' : 'Inactivo' }}
            </td>
            <td>
              <button 
                @click="toggleActivo(j.id)" 
                :class="['btn-toggle', j.activo ? 'activo' : 'inactivo']"
              >
                {{ j.activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const jugadores = ref([])
const nombreInput = ref(null)

const jugador = reactive({
  nombre: '',
  apellidos: '',
  club: '',
  campeonatoId: campeonatoId
})

const focusNombreInput = () => {
  if (nombreInput.value) {
    nombreInput.value.focus()
  }
}

const cargarJugadores = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/jugadores/')
    if (response.ok) {
      const nuevosJugadores = await response.json()
      // Ordenar jugadores por ID de forma descendente
      nuevosJugadores.sort((a, b) => b.id - a.id)
      
      // Mantener el estado de los jugadores existentes
      if (jugadores.value.length > 0) {
        const jugadoresActualizados = nuevosJugadores.map(nuevoJugador => {
          const jugadorExistente = jugadores.value.find(j => j.id === nuevoJugador.id)
          if (jugadorExistente) {
            return { ...nuevoJugador, activo: jugadorExistente.activo }
          }
          return nuevoJugador
        })
        jugadores.value = jugadoresActualizados
      } else {
        jugadores.value = nuevosJugadores
      }
    } else {
      console.error('Error al cargar jugadores')
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const toggleActivo = async (jugadorId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/jugadores/${jugadorId}/toggle-activo`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (response.ok) {
      const jugadorActualizado = await response.json()
      // Actualizar el estado en la lista local
      const jugador = jugadores.value.find(j => j.id === jugadorId)
      if (jugador) {
        jugador.activo = jugadorActualizado.activo
      }
    } else {
      alert('Error al cambiar el estado del jugador')
    }
  } catch (error) {
    console.error('Error:', error)
    alert('Error al cambiar el estado del jugador')
  }
}

const guardarJugador = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/jugadores/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nombre: jugador.nombre,
        apellidos: jugador.apellidos,
        club: jugador.club,
        campeonato_id: parseInt(jugador.campeonatoId)
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      alert(errorData.detail)
      // Refrescar la página si el error es de jugador duplicado
      if (errorData.detail.includes('ya está inscrito en este campeonato')) {
        window.location.reload()
      }
      return
    }

    const nuevoJugador = await response.json()
    jugadores.value.unshift(nuevoJugador)
    
    // Limpiar el formulario
    Object.assign(jugador, {
      nombre: '',
      apellidos: '',
      club: '',
      campeonatoId: campeonatoId
    })
    
    // Mostrar mensaje de éxito
    alert('Jugador inscrito correctamente')
    
    // Poner el foco en el input de nombre
    focusNombreInput()
  } catch (error) {
    console.error('Error:', error)
    alert('Error al inscribir el jugador')
  }
}

const finalizarInscripcion = () => {
  // Implementa la lógica para finalizar la inscripción
  alert('Finalizar Inscripción')
}

// Cargar jugadores y poner foco en el input al montar el componente
onMounted(() => {
  cargarJugadores()
  focusNombreInput()
})
</script>

<style scoped>
.inscripcion-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.btn-finalizar {
  width: 100%;
  background-color: #dc3545;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  transition: background-color 0.3s;
}

.btn-finalizar:hover {
  background-color: #c82333;
}

.inscripcion-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-control {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.btn-submit {
  background-color: #4CAF50;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-submit:hover {
  background-color: #45a049;
}

.jugadores-list {
  margin-top: 30px;
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
}

.btn-toggle {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-toggle.activo {
  background-color: #dc3545;
  color: white;
}

.btn-toggle.inactivo {
  background-color: #28a745;
  color: white;
}

.btn-toggle:hover {
  opacity: 0.9;
}

.estado {
  font-weight: bold;
}

.estado-activo {
  color: #28a745;
}

.estado-inactivo {
  color: #dc3545;
}
</style> 