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
    const response = await fetch('http://localhost:8000/api/campeonatos/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nombre: campeonato.value.nombre,
        fecha_inicio: campeonato.value.fecha_inicio,
        dias_duracion: parseInt(campeonato.value.dias_duracion),
        numero_partidas: parseInt(campeonato.value.numero_partidas)
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error al crear el campeonato');
    }

    const data = await response.json();
    
    // Guardar el campeonato seleccionado en localStorage
    localStorage.setItem('campeonatoSeleccionado', JSON.stringify(data));
    
    // Mostrar mensaje de éxito
    alert('Campeonato creado exitosamente');
    
    // Redirigir a inicio y recargar la página
    router.push('/').then(() => {
      window.location.reload();
    });
  } catch (error) {
    console.error('Error al crear el campeonato:', error);
    alert(error.message || 'Error al crear el campeonato');
  }
};
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