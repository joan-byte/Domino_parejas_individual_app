<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/" class="nav-link" @click="limpiarCampeonato">Inicio</router-link>
        <router-link 
          v-if="!campeonatoSeleccionado" 
          to="/crear-campeonato" 
          class="nav-link"
        >
          Crear Campeonato
        </router-link>
      </div>
      <div v-if="campeonatoSeleccionado" class="nav-right">
        <router-link 
          :to="`/inscripcion/${campeonatoSeleccionado.id}`" 
          class="nav-link"
        >
          Inscripción
        </router-link>
        
        <div class="dropdown">
          <button class="nav-link dropdown-toggle">
            Mesas
            <span class="arrow">▼</span>
          </button>
          <div class="dropdown-content">
            <div class="dropdown-menu" aria-labelledby="navbarDropdownMesas">
              <router-link :to="`/mesas/asignacion/${campeonatoSeleccionado.id}`" class="dropdown-item">Asignación</router-link>
              <router-link :to="`/mesas/registro/${campeonatoSeleccionado.id}`" class="dropdown-item">Registro</router-link>
              <router-link :to="`/mesas/imprimir/${campeonatoSeleccionado.id}`" class="dropdown-item">Imprimir Mesas</router-link>
            </div>
          </div>
        </div>

        <div class="dropdown">
          <button class="nav-link dropdown-toggle">
            Resultados
            <span class="arrow">▼</span>
          </button>
          <div class="dropdown-content">
            <router-link :to="`/resultados/ranking/${campeonatoSeleccionado.id}`" class="dropdown-item">Ranking</router-link>
            <router-link :to="`/resultados/podium/${campeonatoSeleccionado.id}`" class="dropdown-item">Podium</router-link>
            <router-link :to="`/resultados/ranking/imprimir/${campeonatoSeleccionado.id}`" class="dropdown-item">Imprimir Ranking</router-link>
          </div>
        </div>
      </div>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Campeonato {
  id: number
  nombre: string
  fecha_inicio: string
  dias_duracion: number
  numero_partidas: number
  activo: boolean
  partida_actual: number
}

const campeonatoSeleccionado = ref<Campeonato | null>(null)

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    try {
      const campeonato = JSON.parse(campeonatoGuardado)
      campeonatoSeleccionado.value = campeonato
    } catch (error) {
      console.error('Error al parsear el campeonato:', error)
      localStorage.removeItem('campeonatoSeleccionado')
      campeonatoSeleccionado.value = null
    }
  } else {
    campeonatoSeleccionado.value = null
  }
}

const limpiarCampeonato = () => {
  localStorage.removeItem('campeonatoSeleccionado')
  campeonatoSeleccionado.value = null
  window.dispatchEvent(new Event('storage'))
}

const handleStorageChange = () => {
  checkCampeonatoSeleccionado()
}

onMounted(() => {
  checkCampeonatoSeleccionado()
  window.addEventListener('storage', handleStorageChange)
  
  // Vue automáticamente ejecutará esta función cuando el componente se desmonte
  return () => {
    window.removeEventListener('storage', handleStorageChange)
  }
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  padding-top: 80px; /* Espacio para la navbar fija */
}

/* Estilos para impresión */
@media print {
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: white !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  #app {
    padding-top: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    background: white !important;
    position: relative !important;
    min-height: auto !important;
    height: auto !important;
    width: auto !important;
    overflow: visible !important;
  }

  .navbar {
    display: none !important;
  }

  /* Asegurar que no hay márgenes ni padding que interfieran */
  .print-only * {
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    background: white !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}

.navbar {
  background-color: #4CAF50;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 64px; /* Altura fija para la navbar */
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
  font-weight: 800 !important;
  font-size: 1.3rem !important;
}

.nav-link:hover {
  background-color: #45a049;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.arrow {
  font-size: 0.8em;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: white;
  min-width: 160px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  border-radius: 4px;
  z-index: 1;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-item {
  color: #2c3e50;
  padding: 0.8rem 1rem;
  text-decoration: none;
  display: block;
  transition: background-color 0.3s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}
</style>
