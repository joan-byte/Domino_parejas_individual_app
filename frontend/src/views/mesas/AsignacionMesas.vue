<template>
  <div class="asignacion-mesas">
    <div class="header">
      <h2>Asignación de Mesas</h2>
      <div class="header-actions">
        <button class="btn-imprimir" @click="imprimirMesas">
          <i class="fas fa-print"></i> Imprimir
        </button>
        <div class="partida-info">
          <span>Partida: {{ partidaActual }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="jugadoresPaginados.length > 0" class="no-print">
      <table class="jugadores-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>Club</th>
            <th>Mesa</th>
            <th>Pareja</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="jugador in jugadoresPaginados" :key="jugador.id">
            <td>{{ jugador.id }}</td>
            <td>{{ jugador.nombre }}</td>
            <td>{{ jugador.apellidos }}</td>
            <td>{{ jugador.club }}</td>
            <td>{{ jugador.mesa }}</td>
            <td>{{ jugador.numero_pareja }}</td>
          </tr>
        </tbody>
      </table>
      <div class="paginacion-info">
        Página {{ paginaActual + 1 }} de {{ totalPaginas }}
      </div>
    </div>

    <div class="print-only">
      <div v-for="(mesasPar, index) in mesasParaImprimir" :key="index" class="print-page">
        <div v-for="mesa in mesasPar" :key="mesa.numero" class="print-mesa">
          <div class="mesa-header">
            <h3>CAMPEONATO</h3>
            <h4>{{ campeonatoSeleccionado?.nombre }}</h4>
            <div class="mesa-info">
              <span>Partida {{ partidaActual }}</span>
              <span>Mesa {{ mesa.numero }}</span>
            </div>
          </div>
          <div class="parejas-container">
            <div class="pareja">
              <div class="jugador">
                <span>{{ mesa.pareja1?.jugador1?.nombre }} {{ mesa.pareja1?.jugador1?.apellidos }}</span>
                <div class="puntos">
                  <span>PG {{ mesa.pareja1?.jugador1?.PG || 0 }}</span>
                  <span>PP {{ mesa.pareja1?.jugador1?.PP || 150 }}</span>
                </div>
              </div>
              <div class="jugador">
                <span>{{ mesa.pareja1?.jugador2?.nombre }} {{ mesa.pareja1?.jugador2?.apellidos }}</span>
                <div class="puntos">
                  <span>PG {{ mesa.pareja1?.jugador2?.PG || 0 }}</span>
                  <span>PP {{ mesa.pareja1?.jugador2?.PP || 150 }}</span>
                </div>
              </div>
            </div>
            <div class="lineas">
              <div v-for="n in 15" :key="n" class="linea">
                <span class="numero">{{ n }}</span>
                <div class="linea-pareja1"></div>
                <div class="linea-pareja2"></div>
              </div>
            </div>
            <div class="totales">
              <div class="total">Total</div>
              <div class="total">Total</div>
            </div>
            <div class="firmas">
              <div class="firma">Firma</div>
              <div class="firma">Firma</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="jugadoresPaginados.length === 0" class="no-print">
      <p>No hay jugadores asignados todavía.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])
const paginaActual = ref(0)
const jugadoresPorPagina = 15
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(1)
let intervaloAutomatico = null

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
  }
}

// Procesar los jugadores y sus mesas asignadas
const jugadoresOrdenados = computed(() => {
  if (!parejas.value || !Array.isArray(parejas.value)) {
    return []
  }

  // Usar un Map para asegurarnos de que cada jugador aparezca solo una vez
  const jugadoresMap = new Map()

  parejas.value.forEach(pareja => {
    // Solo procesar parejas válidas
    if (pareja.jugador1 && pareja.jugador2 && pareja.mesa && pareja.numero_pareja) {
      // Jugador 1
      if (!jugadoresMap.has(pareja.jugador1_id)) {
        jugadoresMap.set(pareja.jugador1_id, {
          id: pareja.jugador1_id,
          nombre: pareja.jugador1.nombre || '',
          apellidos: pareja.jugador1.apellidos || '',
          club: pareja.jugador1.club || '',
          mesa: pareja.mesa,
          numero_pareja: pareja.numero_pareja
        })
      }
      
      // Jugador 2
      if (!jugadoresMap.has(pareja.jugador2_id)) {
        jugadoresMap.set(pareja.jugador2_id, {
          id: pareja.jugador2_id,
          nombre: pareja.jugador2.nombre || '',
          apellidos: pareja.jugador2.apellidos || '',
          club: pareja.jugador2.club || '',
          mesa: pareja.mesa,
          numero_pareja: pareja.numero_pareja
        })
      }
    }
  })

  // Convertir el Map a array y ordenar por ID
  return Array.from(jugadoresMap.values()).sort((a, b) => a.id - b.id)
})

const totalPaginas = computed(() => {
  return Math.ceil(jugadoresOrdenados.value.length / jugadoresPorPagina)
})

const jugadoresPaginados = computed(() => {
  const inicio = paginaActual.value * jugadoresPorPagina
  const fin = inicio + jugadoresPorPagina
  return jugadoresOrdenados.value.slice(inicio, fin)
})

const siguientePagina = () => {
  if (paginaActual.value < totalPaginas.value - 1) {
    paginaActual.value++
  } else {
    paginaActual.value = 0 // Volver al inicio
  }
}

const iniciarPaginacionAutomatica = () => {
  // Limpiar intervalo existente si hay uno
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  
  // Crear nuevo intervalo
  intervaloAutomatico = setInterval(() => {
    siguientePagina()
  }, 10000) // 10 segundos
}

const cargarParejas = async () => {
  try {
    // Asegurarse de que tenemos el campeonato y la partida actual
    checkCampeonatoSeleccionado()
    if (!campeonatoSeleccionado.value) {
      console.error('No hay campeonato seleccionado')
      return
    }

    // Asegurarse de que la partida actual es un número
    const partida = campeonatoSeleccionado.value.partida_actual || 1
    if (typeof partida !== 'number') {
      console.error('La partida actual no es válida:', partida)
      return
    }

    partidaActual.value = partida

    const response = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partida}`)
    if (response.ok) {
      const data = await response.json()
      parejas.value = data
      
      // Iniciar paginación automática después de cargar los datos
      if (jugadoresOrdenados.value.length > jugadoresPorPagina) {
        iniciarPaginacionAutomatica()
      }
    } else {
      console.error('Error al cargar las parejas:', response.statusText)
      parejas.value = []
    }
  } catch (error) {
    console.error('Error al cargar las parejas:', error)
    parejas.value = []
  }
}

// Agregar un watcher para recargar cuando cambie la partida actual
watch(() => campeonatoSeleccionado.value?.partida_actual, (newPartida) => {
  if (newPartida) {
    partidaActual.value = newPartida
    cargarParejas()
  }
})

onMounted(() => {
  checkCampeonatoSeleccionado()
  if (campeonatoSeleccionado.value) {
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 1
  }
  cargarParejas()
  
  // Agregar listener para cambios en el localStorage
  window.addEventListener('storage', () => {
    checkCampeonatoSeleccionado()
    cargarParejas()
  })
})

onUnmounted(() => {
  // Limpiar el intervalo y el listener cuando el componente se desmonte
  if (intervaloAutomatico) {
    clearInterval(intervaloAutomatico)
  }
  window.removeEventListener('storage', () => {
    checkCampeonatoSeleccionado()
    cargarParejas()
  })
})

// Nuevo computed para organizar las mesas en pares para la impresión
const mesasParaImprimir = computed(() => {
  const mesas = []
  const mesasMap = new Map()

  // Agrupar parejas por mesa
  parejas.value.forEach(pareja => {
    if (!mesasMap.has(pareja.mesa)) {
      mesasMap.set(pareja.mesa, {
        numero: pareja.mesa,
        pareja1: null,
        pareja2: null
      })
    }
    const mesa = mesasMap.get(pareja.mesa)
    if (pareja.numero_pareja === 1) {
      mesa.pareja1 = pareja
    } else {
      mesa.pareja2 = pareja
    }
  })

  // Convertir el Map a array y filtrar mesas incompletas
  const mesasArray = Array.from(mesasMap.values())
    .filter(mesa => mesa.pareja1 && mesa.pareja2)
    .sort((a, b) => a.numero - b.numero)

  // Agrupar mesas en pares
  for (let i = 0; i < mesasArray.length; i += 2) {
    if (i + 1 < mesasArray.length) {
      mesas.push([mesasArray[i], mesasArray[i + 1]])
    } else if (i + 1 === mesasArray.length) {
      // Si queda una mesa suelta y está completa, la añadimos sola
      mesas.push([mesasArray[i]])
    }
  }

  return mesas
})

const imprimirMesas = () => {
  window.print()
}
</script>

<style scoped>
/* Estilos para la vista normal */
.asignacion-mesas {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-imprimir {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-imprimir:hover {
  background-color: #45a049;
}

.partida-info {
  font-size: 1.2em;
  font-weight: bold;
  color: #4CAF50;
}

.jugadores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  margin-bottom: 20px;
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
  color: #2c3e50;
}

.jugadores-table tr:hover {
  background-color: #f8f9fa;
}

.paginacion-info {
  text-align: center;
  margin-top: 10px;
  font-size: 1.1em;
  color: #666;
}

.print-only {
  display: none;
}

/* Estilos para la impresión */
@media print {
  @page {
    size: landscape;
    margin: 0;
  }

  /* Ocultar navbar y otros elementos */
  nav, .navbar, .no-print {
    display: none !important;
  }

  body {
    margin: 0;
    padding: 0;
  }

  .print-only {
    display: block;
    width: 100%;
    height: 100%;
  }

  .print-page {
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: space-between;
    padding: 20px;
    page-break-after: always;
    box-sizing: border-box;
  }

  .print-mesa {
    width: 48%;
    border: 2px solid #000;
    padding: 20px;
    display: flex;
    flex-direction: column;
  }

  .mesa-header {
    border-bottom: 2px solid #000;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }

  .mesa-header h3 {
    margin: 0;
    font-size: 24px;
    font-weight: bold;
    text-align: left;
  }

  .mesa-header h4 {
    margin: 0;
    font-size: 18px;
    font-weight: normal;
    text-align: left;
  }

  .mesa-info {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 16px;
  }

  .parejas-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }

  .pareja {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .jugador {
    display: flex;
    flex-direction: column;
  }

  .jugador span {
    font-size: 16px;
    margin-bottom: 5px;
  }

  .puntos {
    display: flex;
    gap: 20px;
  }

  .lineas {
    margin-top: 20px;
  }

  .linea {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
  }

  .numero {
    width: 30px;
    text-align: right;
    margin-right: 10px;
    font-size: 14px;
  }

  .linea-pareja1,
  .linea-pareja2 {
    flex: 1;
    height: 1px;
    border-bottom: 1px solid #000;
    margin: 0 10px;
  }

  .totales {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    padding-top: 10px;
    border-top: 2px solid #000;
  }

  .total {
    font-size: 16px;
    font-weight: bold;
    width: 45%;
  }

  .firmas {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }

  .firma {
    width: 45%;
    border-top: 2px solid #000;
    padding-top: 5px;
    font-size: 16px;
  }
}
</style> 