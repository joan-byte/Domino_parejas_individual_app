<template>
  <div class="inscripcion-container">
    <button 
      v-if="inscripcionFinalizada"
      :class="['btn-accion', 'btn-volver']"
      @click="volverAtras"
      :disabled="hayResultados"
      :title="hayResultados ? 'No se puede volver atrás porque hay resultados registrados' : 'Eliminar asignaciones y volver a la inscripción'"
    >
      Volver Atrás
    </button>
    <button 
      v-else
      class="btn-accion btn-finalizar"
      @click="finalizarInscripcion"
    >
      Finalizar Inscripción
    </button>

    <div v-if="!inscripcionFinalizada">
      <h2>{{ jugadorSeleccionado ? 'Modificar Jugador' : 'Inscripción de Jugador' }}</h2>
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
            pattern="[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\\s'\\-\\.]+"
            title="Solo letras (incluyendo acentos), espacios y caracteres especiales permitidos"
            @input="validarCampo($event, 'nombre')"
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
            pattern="[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\\s'\\-\\.]+"
            title="Solo letras (incluyendo acentos), espacios y caracteres especiales permitidos"
            @input="validarCampo($event, 'apellidos')"
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
            pattern="[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\\s'\\-\\.]+"
            title="Solo letras (incluyendo acentos), espacios y caracteres especiales permitidos"
            @input="validarCampo($event, 'club')"
          >
        </div>

        <div class="button-group">
          <button 
            v-if="jugadorSeleccionado" 
            type="button" 
            class="btn-cancel" 
            @click="cancelarEdicion"
          >
            Cancelar
          </button>
          <button type="submit" class="btn-submit" :disabled="!formularioValido">
            {{ jugadorSeleccionado ? 'Guardar Cambios' : 'Inscribir Jugador' }}
          </button>
          <button 
            v-if="jugadorSeleccionado" 
            type="button" 
            class="btn-delete" 
            @click="eliminarJugador"
          >
            Eliminar Jugador
          </button>
        </div>
      </form>
    </div>

    <div v-if="inscripcionFinalizada" class="sorteo-realizado">
      <h2>Sorteo Inicial Realizado</h2>
      <p>El sorteo inicial ha sido completado. Las parejas y mesas han sido asignadas aleatoriamente.</p>
      <p>Puede ver los resultados en la sección de Mesas.</p>
    </div>

    <div class="jugadores-list">
      <h3>Jugadores Inscritos</h3>
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Estado</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="j in jugadores" 
            :key="j.id"
            :class="{ 'selected': jugadorSeleccionado?.id === j.id }"
            @click="seleccionarJugador(j)"
          >
            <td>{{ j.id }}</td>
            <td>{{ j.nombre }}</td>
            <td>{{ j.apellidos }}</td>
            <td>{{ j.club }}</td>
            <td :class="['estado', j.activo ? 'estado-activo' : 'estado-inactivo']">
              {{ j.activo ? 'Activo' : 'Inactivo' }}
            </td>
            <td>
              <button 
                @click.stop="toggleActivo(j.id)" 
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
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const campeonatoId = route.params.campeonatoId
const jugadores = ref([])
const nombreInput = ref(null)
const inscripcionFinalizada = ref(false)
const hayResultados = ref(false)
const jugadorSeleccionado = ref(null)

const jugador = ref({
  nombre: '',
  apellidos: '',
  club: '',
  campeonato_id: campeonatoId
})

const focusNombreInput = () => {
  if (nombreInput.value) {
    nombreInput.value.focus()
  }
}

const cargarJugadores = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/jugadores/campeonato/${campeonatoId}`)
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

const seleccionarJugador = (j) => {
  jugadorSeleccionado.value = j
  jugador.value = { ...j }
}

const cancelarEdicion = () => {
  jugadorSeleccionado.value = null
  jugador.value = {
    nombre: '',
    apellidos: '',
    club: '',
    campeonato_id: route.params.campeonatoId
  }
  focusNombreInput()
}

const eliminarJugador = async () => {
  if (!jugadorSeleccionado.value) return
  
  if (confirm('¿Está seguro de que desea eliminar este jugador?')) {
    try {
      await axios.delete(`http://localhost:8000/api/jugadores/${jugadorSeleccionado.value.id}`)
      await cargarJugadores()
      cancelarEdicion()
      alert('Jugador eliminado exitosamente')
    } catch (error) {
      console.error('Error al eliminar jugador:', error)
      alert('Error al eliminar el jugador')
    }
  }
}

const guardarJugador = async () => {
  try {
    if (jugadorSeleccionado.value) {
      // Actualizar jugador existente
      await axios.put(`http://localhost:8000/api/jugadores/${jugadorSeleccionado.value.id}`, jugador.value)
      alert('Jugador actualizado exitosamente')
    } else {
      // Crear nuevo jugador
      await axios.post('http://localhost:8000/api/jugadores/', jugador.value)
    }
    
    await cargarJugadores()
    cancelarEdicion()
    focusNombreInput()
  } catch (error) {
    console.error('Error al guardar jugador:', error)
    let mensajeError = 'Error al guardar el jugador'
    if (error.response?.data?.detail) {
      mensajeError = error.response.data.detail
    }
    alert(mensajeError)
  }
}

const finalizarInscripcion = async () => {
  // Verificar que hay suficientes jugadores activos (mínimo 4 para formar una mesa)
  const jugadoresActivos = jugadores.value.filter(j => j.activo && j.campeonato_id === parseInt(campeonatoId))
  if (jugadoresActivos.length < 4) {
    alert('Se necesitan al menos 4 jugadores activos para realizar el sorteo')
    return
  }

  try {
    // Realizar el sorteo inicial
    const response = await fetch('http://localhost:8000/api/parejas-partida/sorteo-inicial/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        campeonato_id: parseInt(campeonatoId),
        jugadores: jugadoresActivos.map(j => j.id)
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error al realizar el sorteo inicial')
    }

    // Actualizar el estado del campeonato en localStorage
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      const campeonato = JSON.parse(campeonatoGuardado)
      campeonato.partida_actual = 1
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
      window.dispatchEvent(new Event('storage'))
    }

    inscripcionFinalizada.value = true
  } catch (error) {
    console.error('Error:', error)
    alert(error.message || 'Error al realizar el sorteo inicial')
  }
}

const verificarSorteoYResultados = async () => {
  try {
    // Verificar si existe el sorteo inicial
    const responseSorteo = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/1`)
    if (responseSorteo.ok) {
      const parejas = await responseSorteo.json()
      inscripcionFinalizada.value = parejas.length > 0
    }

    // Verificar si hay resultados
    const responseResultados = await fetch(`http://localhost:8000/api/resultados/campeonato/${campeonatoId}/partida/1`)
    if (responseResultados.ok) {
      const resultados = await responseResultados.json()
      hayResultados.value = resultados.length > 0
      console.log('Hay resultados:', hayResultados.value)
    }
  } catch (error) {
    console.error('Error al verificar estado:', error)
  }
}

const volverAtras = async () => {
  if (hayResultados.value) return

  try {
    // Eliminar las asignaciones de parejas y mesas
    const response = await fetch(`http://localhost:8000/api/parejas-partida/eliminar/${campeonatoId}/1`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error('Error al eliminar las asignaciones')
    }

    inscripcionFinalizada.value = false
    alert('Las asignaciones han sido eliminadas. Puede realizar un nuevo sorteo.')
  } catch (error) {
    console.error('Error:', error)
    alert('Error al eliminar las asignaciones')
  }
}

const validarCampo = (event, campo) => {
  const patron = /^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\\s'\\-\\.]*$/
  const valor = event.target.value
  
  if (!patron.test(valor)) {
    // Si el valor no coincide con el patrón, eliminar el último carácter
    jugador[campo] = valor.slice(0, -1)
  }
}

const formularioValido = computed(() => {
  const patron = /^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\\s'\\-\\.]+$/
  return patron.test(jugador.nombre) && 
         patron.test(jugador.apellidos) &&
         (!jugador.club || patron.test(jugador.club))
})

onMounted(async () => {
  await verificarSorteoYResultados()
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

.btn-accion {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  transition: background-color 0.3s;
}

.btn-finalizar {
  background-color: #dc3545;
  color: white;
}

.btn-finalizar:hover {
  background-color: #c82333;
}

.btn-volver {
  background-color: #fd7e14;
  color: white;
}

.btn-volver:hover {
  background-color: #e76b00;
}

.btn-volver:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #f0f0f0 !important;
  color: #666 !important;
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

.sorteo-realizado {
  text-align: center;
  margin-top: 2rem;
}

.sorteo-realizado h2 {
  color: #28a745;
  margin-bottom: 1rem;
}

.sorteo-realizado p {
  color: #666;
  margin-bottom: 0.5rem;
}

.selected {
  background-color: #e8f5e9;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-delete:hover {
  background-color: #c82333;
}
</style>