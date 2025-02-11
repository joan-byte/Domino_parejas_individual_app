<template>
  <div class="home">
    <div class="header">
      <h1>Dominó por Parejas Individual</h1>
    </div>
    
    <div class="campeonatos-list" v-if="campeonatos.length > 0">
      <div class="campeonatos-grid">
        <div 
          v-for="campeonato in campeonatos" 
          :key="campeonato.id" 
          class="campeonato-card"
          :class="{ 'selected': campeonatoSeleccionado?.id === campeonato.id }"
          @click="seleccionarCampeonato(campeonato)"
        >
          <div class="card-header">
            <h2>{{ campeonato.nombre }}</h2>
            <div class="estado-campeonato">
              <span v-if="campeonato.finalizado" class="estado finalizado">Finalizado</span>
              <span v-else-if="campeonato.partida_actual !== 'No hay registros'" class="estado activo">En curso</span>
            </div>
          </div>
          <div class="card-content">
            <p><strong>Fecha de inicio:</strong> {{ formatDate(campeonato.fecha_inicio) }}</p>
            <p><strong>Duración:</strong> {{ campeonato.dias_duracion }} días</p>
            <p><strong>Partidas:</strong> {{ campeonato.numero_partidas }}</p>
            <p><strong>Puntos Máximos:</strong> {{ campeonato.PM }}</p>
            <p><strong>Partida actual:</strong> {{ campeonato.partida_actual }}</p>
          </div>
          <div class="button-group">
            <button 
              class="btn-modificar" 
              @click.stop="modificarCampeonato(campeonato.id)"
            >
              Modificar
            </button>
            <button 
              class="btn-eliminar" 
              @click.stop="eliminarCampeonato(campeonato.id)"
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="no-campeonatos" v-else>
      <p>No hay campeonatos activos en este momento.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const campeonatos = ref([])
const campeonatoSeleccionado = ref(null)

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('es-ES', options)
}

// Función para verificar el estado de selección
const verificarSeleccion = () => {
  if (route.path === '/') {
    campeonatoSeleccionado.value = null
  } else {
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    }
  }
}

const seleccionarCampeonato = (campeonato) => {
  if (route.path === '/') {
    campeonatoSeleccionado.value = campeonato
    localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
    window.dispatchEvent(new Event('storage'))
  }
}

const modificarCampeonato = (id) => {
  router.push(`/modificar-campeonato/${id}`)
}

const eliminarCampeonato = async (id) => {
  if (confirm('¿Está seguro de que desea eliminar este campeonato?')) {
    try {
      const response = await axios.delete(`http://localhost:8000/api/campeonatos/${id}`, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })
      
      if (response.status === 204) {
        if (campeonatoSeleccionado.value?.id === id) {
          campeonatoSeleccionado.value = null
          localStorage.removeItem('campeonatoSeleccionado')
          // Disparar evento storage para actualizar otros componentes
          window.dispatchEvent(new Event('storage'))
        }
        alert('Campeonato eliminado exitosamente')
        await cargarCampeonatos()
      }
    } catch (error) {
      console.error('Error al eliminar el campeonato:', error)
      let mensajeError = 'Error al eliminar el campeonato'
      if (error.response) {
        // El servidor respondió con un código de error
        mensajeError = error.response.data?.detail || mensajeError
      } else if (error.request) {
        // La petición fue hecha pero no se recibió respuesta
        mensajeError = 'No se pudo conectar con el servidor'
      }
      alert(mensajeError)
    }
  }
}

// Función para actualizar un campeonato específico
const actualizarCampeonatoEnLista = (campeonatoId, nuevaPartida) => {
  const campeonato = campeonatos.value.find(c => c.id === campeonatoId)
  if (campeonato) {
    campeonato.partida_actual = nuevaPartida
  }
}

const actualizarPartidaActual = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    const campeonato = JSON.parse(campeonatoGuardado)
    campeonatoSeleccionado.value = campeonato
    // Actualizar también en la lista de campeonatos
    actualizarCampeonatoEnLista(campeonato.id, campeonato.partida_actual)
  }
}

// Actualizar cuando cambie el localStorage
window.addEventListener('storage', () => {
  if (route.path === '/') {
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    campeonatoSeleccionado.value = campeonatoGuardado ? JSON.parse(campeonatoGuardado) : null
  }
})

// Limpiar selección cuando se navega a la página de inicio
watch(() => route.path, async (newPath) => {
  if (newPath === '/') {
    campeonatoSeleccionado.value = null
    localStorage.removeItem('campeonatoSeleccionado')
    await cargarCampeonatos()
  }
})

const cargarCampeonatos = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/campeonatos/')
    const campeonatosData = response.data

    for (const campeonato of campeonatosData) {
      try {
        const responsePartidas = await axios.get(`http://localhost:8000/api/parejas-partida/ultima-partida/${campeonato.id}`)
        if (responsePartidas.data.tiene_registros) {
          campeonato.partida_actual = responsePartidas.data.ultima_partida
        } else {
          campeonato.partida_actual = 0
        }
      } catch (error) {
        console.error(`Error al obtener la última partida del campeonato ${campeonato.id}:`, error)
        campeonato.partida_actual = "Error al obtener partida"
      }
    }

    campeonatos.value = campeonatosData
    // Verificar si hay un campeonato seleccionado después de cargar los datos
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado && route.path === '/') {
      campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    }
  } catch (error) {
    console.error('Error al cargar los campeonatos:', error)
  }
}

onMounted(async () => {
  if (route.path === '/') {
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    }
  }
  await cargarCampeonatos()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

h2 {
  color: #2c3e50;
  margin: 2rem 0 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
  padding: 0.5rem 1rem;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.campeonatos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.campeonato-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.campeonato-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.campeonato-card.selected {
  border-color: #3498db !important;
  background-color: #f7f9fc !important;
}

.campeonato-card h3 {
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.campeonato-info {
  margin-bottom: 1rem;
}

.campeonato-info p {
  margin: 0.5rem 0;
  color: #666;
}

.no-campeonatos {
  text-align: center;
  color: #666;
  margin: 3rem 0;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-modificar {
  flex: 1;
  background-color: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-eliminar {
  flex: 1;
  background-color: #e74c3c;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-modificar:hover {
  background-color: #2980b9;
}

.btn-eliminar:hover {
  background-color: #c0392b;
}

.estado-campeonato {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: bold;
}

.estado {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: bold;
}

.estado.finalizado {
  background-color: #dc3545;
  color: white;
}

.estado.activo {
  background-color: #28a745;
  color: white;
}

.btn-seleccionar:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style> 