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

      <div class="form-group">
        <label for="PM">Puntos Máximos</label>
        <input 
          type="number" 
          id="PM" 
          v-model.number="campeonato.PM"
          required
          min="0"
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

const router = useRouter()

const campeonato = ref({
  nombre: '',
  fecha_inicio: '',
  dias_duracion: 1,
  numero_partidas: 1,
  PM: 300
})

const crearCampeonato = async () => {
  try {
    // Validaciones iniciales
    if (!campeonato.value.nombre || !campeonato.value.fecha_inicio || 
        !campeonato.value.dias_duracion || !campeonato.value.numero_partidas) {
      alert('Por favor, complete todos los campos requeridos');
      return;
    }

    if (campeonato.value.dias_duracion <= 0 || campeonato.value.numero_partidas <= 0) {
      alert('La duración y el número de partidas deben ser mayores que 0');
      return;
    }

    const nombreLimpio = campeonato.value.nombre.trim();
    if (nombreLimpio === '') {
      alert('El nombre del campeonato no puede estar vacío');
      return;
    }

    // Verificar campeonatos existentes
    const verificarResponse = await fetch('/api/campeonatos/');
    if (!verificarResponse.ok) {
      throw new Error('Error al verificar campeonatos existentes');
    }
    const campeonatosExistentes = await verificarResponse.json();
    
    // Formatear la fecha de inicio para la comparación
    const fechaInicio = new Date(campeonato.value.fecha_inicio);
    const fechaInicioStr = fechaInicio.toISOString().split('T')[0];
    
    console.log('Fecha a enviar:', fechaInicioStr);
    console.log('Campeonatos existentes:', campeonatosExistentes);
    
    // Buscar campeonatos con el mismo nombre y fecha
    const campeonatoExistente = campeonatosExistentes.find(c => {
      const fechaExistente = new Date(c.fecha_inicio).toISOString().split('T')[0];
      console.log(`Comparando "${nombreLimpio}" con "${c.nombre}" y fecha ${fechaExistente}`);
      return c.nombre.toLowerCase() === nombreLimpio.toLowerCase() && 
             fechaExistente === fechaInicioStr;
    });

    if (campeonatoExistente) {
      const fechaFormateada = new Date(campeonatoExistente.fecha_inicio).toLocaleDateString();
      alert(`Ya existe un campeonato con el nombre "${nombreLimpio}" en la fecha ${fechaFormateada}`);
      return;
    }

    // Si no hay duplicados exactos, proceder con la creación
    const datosCampeonato = {
      nombre: nombreLimpio,
      fecha_inicio: fechaInicioStr,
      dias_duracion: parseInt(campeonato.value.dias_duracion),
      numero_partidas: parseInt(campeonato.value.numero_partidas),
      PM: parseInt(campeonato.value.PM || 300)
    };

    console.log('Datos completos a enviar:', JSON.stringify(datosCampeonato, null, 2));

    const response = await fetch('/api/campeonatos/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datosCampeonato)
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error response completo:', errorData);
      console.error('Status:', response.status);
      
      if (errorData.detail === 'Error de integridad en la base de datos') {
        alert('Ya existe un campeonato con el mismo nombre y fecha. Por favor, elige una fecha diferente o cambia el nombre.');
      } else {
        throw new Error(errorData.detail || 'Error al crear el campeonato');
      }
      return;
    }

    const data = await response.json();
    console.log('Respuesta exitosa:', data);
    
    localStorage.setItem('campeonatoSeleccionado', JSON.stringify(data));
    alert('Campeonato creado exitosamente');
    router.push('/');
  } catch (error) {
    console.error('Error completo:', error);
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