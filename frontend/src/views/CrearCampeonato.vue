<template>
  <div class="crear-campeonato">
    <h1>Crear Nuevo Campeonato</h1>
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
        <button type="button" class="btn-primary" @click="crearCampeonato">Crear Campeonato</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const campeonato = ref({
  nombre: '',
  fecha_inicio: '',
  dias_duracion: 1,
  numero_partidas: 1
})

const crearCampeonato = async () => {
  try {
    // Validar campos requeridos
    if (!campeonato.value.nombre || !campeonato.value.fecha_inicio || 
        !campeonato.value.dias_duracion || !campeonato.value.numero_partidas) {
      alert('Por favor, complete todos los campos')
      return
    }

    const response = await axios.post('http://localhost:8000/api/campeonatos/', 
      campeonato.value,
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    )

    if (response.status === 201) {
      alert('Campeonato creado exitosamente')
      router.push('/')
    }
  } catch (error) {
    console.error('Error al crear el campeonato:', error)
    let mensajeError = 'Error al crear el campeonato'
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
</script>

<style scoped>
.crear-campeonato {
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