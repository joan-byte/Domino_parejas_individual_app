<template>
  <div class="home">
    <h1>Campeonato de Parejas Individual</h1>
    
    <div class="campeonatos-list" v-if="campeonatos.length > 0">
      <h2>Campeonatos Activos</h2>
      <div class="campeonatos-grid">
        <div 
          v-for="campeonato in campeonatos" 
          :key="campeonato.id" 
          class="campeonato-card"
          :class="{ 'selected': campeonatoSeleccionado?.id === campeonato.id }"
          @click="seleccionarCampeonato(campeonato)"
        >
          <h3>{{ campeonato.nombre }}</h3>
          <div class="campeonato-info">
            <p><strong>Fecha de inicio:</strong> {{ formatDate(campeonato.fecha_inicio) }}</p>
            <p><strong>Duración:</strong> {{ campeonato.dias_duracion }} días</p>
            <p><strong>Partidas:</strong> {{ campeonato.numero_partidas }}</p>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const campeonatos = ref([])
const campeonatoSeleccionado = ref(null)

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('es-ES', options)
}

const seleccionarCampeonato = (campeonato) => {
  campeonatoSeleccionado.value = campeonato
  localStorage.setItem('campeonatoSeleccionado', JSON.stringify(campeonato))
  // Disparar el evento storage para que App.vue detecte el cambio
  window.dispatchEvent(new Event('storage'))
}

const modificarCampeonato = (id) => {
  router.push(`/modificar-campeonato/${id}`)
}

const cargarCampeonatos = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/campeonatos/')
    campeonatos.value = response.data
    
    // Recuperar campeonato seleccionado del localStorage
    const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
    if (campeonatoGuardado) {
      const campeonato = JSON.parse(campeonatoGuardado)
      // Verificar si el campeonato aún existe en la lista
      if (campeonatos.value.some(c => c.id === campeonato.id)) {
        campeonatoSeleccionado.value = campeonato
      } else {
        localStorage.removeItem('campeonatoSeleccionado')
      }
    }
  } catch (error) {
    console.error('Error al cargar los campeonatos:', error)
  }
}

const eliminarCampeonato = async (id) => {
  if (confirm('¿Está seguro de que desea eliminar este campeonato?')) {
    try {
      await axios.delete(`http://localhost:8000/api/campeonatos/${id}`)
      if (campeonatoSeleccionado.value?.id === id) {
        campeonatoSeleccionado.value = null
        localStorage.removeItem('campeonatoSeleccionado')
      }
      alert('Campeonato eliminado exitosamente')
      await cargarCampeonatos()
    } catch (error) {
      console.error('Error al eliminar el campeonato:', error)
      alert('Error al eliminar el campeonato')
    }
  }
}

onMounted(() => {
  cargarCampeonatos()
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
}

.campeonato-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.campeonato-card.selected {
  border: 2px solid #3498db;
  background-color: #f7f9fc;
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
</style> 