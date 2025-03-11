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
            :value="jugador.nombre"
            required 
            class="form-control"
            autocomplete="off"
            @input="(e) => actualizarCampo(e, 'nombre')"
          >
        </div>

        <div class="form-group">
          <label for="apellidos">Apellidos:</label>
          <input 
            type="text" 
            id="apellidos" 
            :value="jugador.apellidos"
            required 
            class="form-control"
            autocomplete="off"
            @input="(e) => actualizarCampo(e, 'apellidos')"
          >
        </div>

        <div class="form-group">
          <label for="club">Club:</label>
          <input 
            type="text" 
            id="club" 
            :value="jugador.club"
            class="form-control"
            autocomplete="off"
            @input="(e) => actualizarCampo(e, 'club')"
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
import { reactive, ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const campeonatoId = ref(route.params.campeonatoId || '')
const jugadores = ref([])
const nombreInput = ref(null)
const inscripcionFinalizada = ref(false)
const hayResultados = ref(false)
const jugadorSeleccionado = ref(null)

const jugador = ref({
  nombre: '',
  apellidos: '',
  club: '',
  campeonato_id: parseInt(route.params.campeonatoId) || 0
})

const focusNombreInput = () => {
  if (nombreInput.value) {
    nombreInput.value.focus()
  }
}

const cargarJugadores = async () => {
  if (!campeonatoId.value) return

  try {
    // Obtener todos los jugadores del campeonato
    const response = await fetch(`http://localhost:8000/api/jugadores/campeonato/${campeonatoId.value}`)
    if (!response.ok) {
      console.error('Error al cargar jugadores')
      return
    }
    
    // Obtener jugadores activos
    const responseActivos = await fetch(`http://localhost:8000/api/jugadores/activos/campeonato/${campeonatoId.value}`)
    if (!responseActivos.ok) {
      console.error('Error al cargar jugadores activos')
      return
    }

    const nuevosJugadores = await response.json()
    const jugadoresActivos = await responseActivos.json()
    const jugadoresActivosIds = new Set(jugadoresActivos.map(j => j.id))

    // Ordenar jugadores por ID de forma descendente y marcar su estado activo
    const jugadoresOrdenados = nuevosJugadores
      .map(jugador => ({
        ...jugador,
        activo: jugadoresActivosIds.has(jugador.id)
      }))
      .sort((a, b) => b.id - a.id)

    jugadores.value = jugadoresOrdenados
    console.log('Jugadores cargados:', jugadores.value)
  } catch (error) {
    console.error('Error:', error)
  }
}

const toggleActivo = async (jugadorId) => {
  try {
    // Si el jugador está activo, lo desactivamos
    const jugador = jugadores.value.find(j => j.id === jugadorId)
    if (jugador?.activo) {
      // Obtener la partida actual del localStorage
      const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
      const campeonato = campeonatoGuardado ? JSON.parse(campeonatoGuardado) : null
      const partidaActual = campeonato?.partida_actual || 1

      console.log('Enviando datos:', {
        partida_actual: partidaActual,
        campeonato_id: parseInt(campeonatoId.value)
      })

      // Llamar al endpoint de desactivación
      const response = await fetch(`http://localhost:8000/api/jugadores/${jugadorId}/desactivar-y-quitar`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          partida_actual: partidaActual,
          campeonato_id: parseInt(campeonatoId.value)
        })
      })

      if (response.ok) {
        const resultado = await response.json()
        console.log('Respuesta del servidor:', resultado)
        // Actualizar el estado en la lista local
        jugador.activo = false
        
        // Disparar evento para actualizar otros componentes
        window.dispatchEvent(new CustomEvent('jugador-desactivado', {
          detail: { jugadorId, campeonatoId: campeonatoId.value }
        }))

        // Recargar la lista de jugadores para asegurar que tenemos el estado más reciente
        await cargarJugadores()
      } else {
        const error = await response.json()
        console.error('Error del servidor:', error)
        throw new Error(error.detail || 'Error al desactivar el jugador')
      }
    } else {
      // Si el jugador está inactivo, lo activamos con el endpoint toggle-activo
      const response = await fetch(`http://localhost:8000/api/jugadores/${jugadorId}/toggle-activo`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (response.ok) {
        const jugadorActualizado = await response.json()
        jugador.activo = jugadorActualizado.activo
        
        // Disparar evento para actualizar otros componentes
        window.dispatchEvent(new CustomEvent('jugador-actualizado', {
          detail: { jugadorId, campeonatoId: campeonatoId.value }
        }))

        // Recargar la lista de jugadores
        await cargarJugadores()
      } else {
        const error = await response.json()
        console.error('Error del servidor:', error)
        throw new Error(error.detail || 'Error al activar el jugador')
      }
    }
  } catch (error) {
    console.error('Error:', error)
    alert(error.message || 'Error al cambiar el estado del jugador')
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
    campeonato_id: parseInt(campeonatoId.value)
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
    const jugadorData = {
      ...jugador.value,
      nombre: jugador.value.nombre.trim(),
      apellidos: jugador.value.apellidos.trim(),
      club: jugador.value.club ? jugador.value.club.trim() : null
    }

    if (jugadorSeleccionado.value) {
      // Actualizar jugador existente
      await axios.put(`http://localhost:8000/api/jugadores/${jugadorSeleccionado.value.id}`, jugadorData)
      alert('Jugador actualizado exitosamente')
    } else {
      // Crear nuevo jugador
      await axios.post('http://localhost:8000/api/jugadores/', jugadorData)
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
  // Obtener array de jugadores activos
  const jugadoresActivos = jugadores.value.filter(j => j.activo);
  
  // Verificar que el número de jugadores activos es múltiplo de 4
  if (jugadoresActivos.length % 4 !== 0) {
    alert('Los jugadores activos deben ser múltiplo de 4');
    return;
  }

  try {
    // Realizar el sorteo inicial usando el array de jugadores activos
    const response = await fetch('http://localhost:8000/api/parejas-partida/sorteo-inicial/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        campeonato_id: parseInt(campeonatoId.value),
        jugadores: jugadoresActivos.map(j => j.id)  // Ahora sí podemos usar map() porque jugadoresActivos es un array
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
      
      // Disparar evento de storage para actualizar otros componentes
      window.dispatchEvent(new Event('storage'))
      
      // Disparar evento específico para actualizar la asignación de mesas
      window.dispatchEvent(new CustomEvent('update-asignacion-mesas'))
      
      console.log('Campeonato actualizado en localStorage con partida_actual = 1')
    }

    inscripcionFinalizada.value = true
    // Redirigir a la vista de asignación de mesas
    router.push(`/mesas/asignacion/${campeonatoId.value}`)
  } catch (error) {
    console.error('Error:', error)
    alert(error.message || 'Error al realizar el sorteo inicial')
  }
}

const verificarSorteoYResultados = async () => {
  try {
    // Verificar si existe el sorteo inicial
    const responseSorteo = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId.value}/partida/1`)
    if (responseSorteo.ok) {
      const parejas = await responseSorteo.json()
      inscripcionFinalizada.value = parejas.length > 0
    }

    // Verificar si hay resultados
    const responseResultados = await fetch(`http://localhost:8000/api/resultados/campeonato/${campeonatoId.value}/partida/1`)
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
    const response = await fetch(`http://localhost:8000/api/parejas-partida/eliminar/${campeonatoId.value}/1`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error('Error al eliminar las asignaciones')
    }

    inscripcionFinalizada.value = false
    
    // Actualizar el estado del campeonato en localStorage
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      const campeonato = JSON.parse(campeonatoGuardado)
      campeonato.partida_actual = 0
      localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
      window.dispatchEvent(new Event('storage'))
    }
    
    alert('Las asignaciones han sido eliminadas. Puede realizar un nuevo sorteo.')
  } catch (error) {
    console.error('Error:', error)
    alert('Error al eliminar las asignaciones')
  }
}

const actualizarCampo = (event, campo) => {
  const valor = event.target.value
  // Permitir solo letras, espacios y caracteres especiales
  const caracteresPermitidos = /^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\s]*$/

  if (campo === 'club') {
    // Para club permitimos también guiones y puntos
    const caracteresClubPermitidos = /^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\s\-\.]*$/
    if (caracteresClubPermitidos.test(valor)) {
      jugador.value[campo] = valor
    }
  } else {
    if (caracteresPermitidos.test(valor)) {
      jugador.value[campo] = valor
    }
  }
}

const formularioValido = computed(() => {
  const nombreValido = jugador.value.nombre.trim().length > 0
  const apellidosValidos = jugador.value.apellidos.trim().length > 0
  // El club es opcional, así que no lo validamos si está vacío
  const clubValido = !jugador.value.club || jugador.value.club.trim().length > 0

  return nombreValido && apellidosValidos && clubValido
})

onMounted(async () => {
  // Verificar si hay un campeonato seleccionado
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (!campeonatoId.value && campeonatoGuardado) {
    const campeonato = JSON.parse(campeonatoGuardado)
    campeonatoId.value = campeonato.id.toString()
    jugador.value.campeonato_id = parseInt(campeonato.id)
  }

  if (!campeonatoId.value) {
    console.error('No hay campeonato seleccionado')
    router.push('/campeonatos')
    return
  }

  // Cargar jugadores antes de verificar sorteo y resultados
  await cargarJugadores()
  await verificarSorteoYResultados()
  focusNombreInput()

  // Añadir listener para recargar jugadores cuando se desactive uno
  window.addEventListener('jugador-desactivado', cargarJugadores)
})

onUnmounted(() => {
  // Limpiar el listener al desmontar el componente
  window.removeEventListener('jugador-desactivado', cargarJugadores)
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