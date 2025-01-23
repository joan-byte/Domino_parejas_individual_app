<template>
  <div class="modificar-campeonato">
    <h1>Modificar Campeonato</h1>
    <form class="campeonato-form">
      <div class="form-group">
        <label for="nombre">Nombre del Campeonato</label>
        <input 
          type="text" 
          id="nombre" 
          v-model="campeonato.nombre" 
          required
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="fecha_inicio">Fecha de Inicio</label>
        <input 
          type="date" 
          id="fecha_inicio" 
          v-model="campeonato.fecha_inicio"
          required
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="dias_duracion">Duración (días)</label>
        <input 
          type="number" 
          id="dias_duracion" 
          v-model.number="campeonato.dias_duracion"
          required
          min="1"
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="numero_partidas">Número de Partidas</label>
        <input 
          type="number" 
          id="numero_partidas" 
          v-model.number="campeonato.numero_partidas"
          required
          min="1"
          class="form-control"
        >
      </div>

      <div class="button-group">
        <button type="button" class="btn-secondary" @click="$router.push('/')">Cancelar</button>
        <button type="button" class="btn-primary" @click="guardarCambios">Guardar</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const campeonato = ref({
  nombre: '',
  fecha_inicio: '',
  dias_duracion: 1,
  numero_partidas: 1
})

const cargarCampeonato = async () => {
  try {
    const id = route.params.id
    const response = await axios.get(`http://localhost:8000/api/v1/campeonatos/${id}`)
    campeonato.value = response.data
  } catch (error) {
    alert('Error al cargar el campeonato')
    router.push('/')
  }
}

const guardarCambios = async () => {
  try {
    const id = route.params.id
    await axios.put(`http://localhost:8000/api/v1/campeonatos/${id}`, campeonato.value)
    alert('Campeonato modificado exitosamente')
    router.push('/')
  } catch (error) {
    alert('Error al modificar el campeonato')
  }
}

onMounted(() => {
  cargarCampeonato()
})
</script>

<style scoped>
.modificar-campeonato {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.campeonato-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

label {
  font-weight: bold;
}
</style> 