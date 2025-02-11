<template>
  <div class="asignacion-mesas">
    <div class="header no-print">
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
      <div class="print-container">
        <template v-for="(mesa, index) in mesasAplanadas" :key="mesa.numero">
          <div v-if="index % 2 === 0" class="print-page">
            <!-- Primera mesa de la página -->
            <div class="print-mesa">
              <div class="mesa-header">
                <div class="header-top">
                  <div class="header-left">
                    <h1>CAMPEONATO</h1>
                    <h2>Social Club Esportiu Garraf</h2>
                  </div>
                  <div class="header-right">
                    <div class="mesa-info">
                      <span>Partida {{ partidaActual }}</span>
                      <span>Mesa {{ mesa.numero }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="parejas-container">
                <div class="jugadores-grid">
                  <div class="pareja-container">
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesa.pareja1?.jugador1?.nombre }} {{ mesa.pareja1?.jugador1?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesa.pareja1?.jugador1?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesa.pareja1?.jugador1?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesa.pareja1?.jugador2?.nombre }} {{ mesa.pareja1?.jugador2?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesa.pareja1?.jugador2?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesa.pareja1?.jugador2?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="pareja-container">
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesa.pareja2?.jugador1?.nombre }} {{ mesa.pareja2?.jugador1?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesa.pareja2?.jugador1?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesa.pareja2?.jugador1?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesa.pareja2?.jugador2?.nombre }} {{ mesa.pareja2?.jugador2?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesa.pareja2?.jugador2?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesa.pareja2?.jugador2?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="lineas-container">
                <div class="lineas-columna">
                  <div class="lineas-wrapper">
                    <div class="lineas">
                      <div v-for="n in 15" :key="n" class="linea">
                        <span class="numero">{{ n }}</span>
                        <div class="linea-contenido"></div>
                      </div>
                    </div>
                    <div class="columna">
                      <div class="total">Total</div>
                      <div class="firma">Firma</div>
                    </div>
                  </div>
                </div>
                <div class="lineas-columna">
                  <div class="lineas-wrapper">
                    <div class="lineas">
                      <div v-for="n in 15" :key="n" class="linea">
                        <span class="numero">{{ n }}</span>
                        <div class="linea-contenido"></div>
                      </div>
                    </div>
                    <div class="columna">
                      <div class="total">Total</div>
                      <div class="firma">Firma</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Segunda mesa de la página (si existe) -->
            <div v-if="index + 1 < mesasAplanadas.length" class="print-mesa">
              <div class="mesa-header">
                <div class="header-top">
                  <div class="header-left">
                    <h1>CAMPEONATO</h1>
                    <h2>Social Club Esportiu Garraf</h2>
                  </div>
                  <div class="header-right">
                    <div class="mesa-info">
                      <span>Partida {{ partidaActual }}</span>
                      <span>Mesa {{ mesasAplanadas[index + 1].numero }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="parejas-container">
                <div class="jugadores-grid">
                  <div class="pareja-container">
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesasAplanadas[index + 1].pareja1?.jugador1?.nombre }} {{ mesasAplanadas[index + 1].pareja1?.jugador1?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesasAplanadas[index + 1].pareja1?.jugador1?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesasAplanadas[index + 1].pareja1?.jugador1?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesasAplanadas[index + 1].pareja1?.jugador2?.nombre }} {{ mesasAplanadas[index + 1].pareja1?.jugador2?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesasAplanadas[index + 1].pareja1?.jugador2?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesasAplanadas[index + 1].pareja1?.jugador2?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="pareja-container">
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesasAplanadas[index + 1].pareja2?.jugador1?.nombre }} {{ mesasAplanadas[index + 1].pareja2?.jugador1?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesasAplanadas[index + 1].pareja2?.jugador1?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesasAplanadas[index + 1].pareja2?.jugador1?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="jugador">
                      <div class="jugador-info">
                        <span class="nombre">{{ mesasAplanadas[index + 1].pareja2?.jugador2?.nombre }} {{ mesasAplanadas[index + 1].pareja2?.jugador2?.apellidos }}</span>
                        <div class="puntos-container">
                          <span class="puntos">PG {{ mesasAplanadas[index + 1].pareja2?.jugador2?.PP || 150 }}</span>
                          <span class="puntos">PC {{ mesasAplanadas[index + 1].pareja2?.jugador2?.PC || 0 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="lineas-container">
                <div class="lineas-columna">
                  <div class="lineas-wrapper">
                    <div class="lineas">
                      <div v-for="n in 15" :key="n" class="linea">
                        <span class="numero">{{ n }}</span>
                        <div class="linea-contenido"></div>
                      </div>
                    </div>
                    <div class="columna">
                      <div class="total">Total</div>
                      <div class="firma">Firma</div>
                    </div>
                  </div>
                </div>
                <div class="lineas-columna">
                  <div class="lineas-wrapper">
                    <div class="lineas">
                      <div v-for="n in 15" :key="n" class="linea">
                        <span class="numero">{{ n }}</span>
                        <div class="linea-contenido"></div>
                      </div>
                    </div>
                    <div class="columna">
                      <div class="total">Total</div>
                      <div class="firma">Firma</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
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

// Computed para tener un array plano de mesas
const mesasAplanadas = computed(() => {
  const mesasMap = new Map()
  
  parejas.value.forEach(pareja => {
    if (!mesasMap.has(pareja.mesa)) {
      mesasMap.set(pareja.mesa, {
        numero: pareja.mesa,
        pareja1: null,
        pareja2: null
      })
    }
    
    const mesaActual = mesasMap.get(pareja.mesa)
    if (pareja.numero_pareja === 1) {
      mesaActual.pareja1 = pareja
    } else if (pareja.numero_pareja === 2) {
      mesaActual.pareja2 = pareja
    }
  })

  // Convertir el Map a array y filtrar mesas completas
  const mesasCompletas = Array.from(mesasMap.values())
    .filter(mesa => mesa.pareja1 && mesa.pareja2)

  // Ordenar las mesas por número
  const mesasOrdenadas = mesasCompletas.sort((a, b) => {
    return parseInt(a.numero) - parseInt(b.numero)
  })

  // Agrupar las mesas en pares secuenciales
  const mesasAgrupadas = []
  for (let i = 0; i < mesasOrdenadas.length; i++) {
    mesasAgrupadas.push(mesasOrdenadas[i])
  }

  // Asegurarnos de que las mesas estén en orden correcto
  return mesasAgrupadas.sort((a, b) => {
    const numA = parseInt(a.numero)
    const numB = parseInt(b.numero)
    if (Math.floor((numA - 1) / 2) === Math.floor((numB - 1) / 2)) {
      return numA - numB
    }
    return Math.floor((numA - 1) / 2) - Math.floor((numB - 1) / 2)
  })
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
    size: A4 landscape;
    margin: 0;
  }

  body {
    margin: 0;
    background-color: white;
  }

  .print-container {
    display: grid;
    grid-template-columns: repeat(2, 130mm);
    gap: 17mm;
    padding: 15mm;
    justify-content: center;
    page-break-after: avoid;
  }

  .print-mesa {
    height: 180mm;
    border: 2px solid black;
    display: flex;
    flex-direction: column;
    break-inside: avoid;
    page-break-inside: avoid;
    padding: 0;
    box-sizing: border-box;
  }

  .lineas-container {
    margin: 0;
    flex: 1;
    display: flex;
    justify-content: space-between;
    gap: 0;
    padding: 0;
    margin-bottom: -2px;
  }

  .lineas-columna {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin: 0;
    border: 2px solid black;
    padding: 3mm;
    margin-bottom: 0;
  }

  .columna {
    width: 100%;
    margin-top: auto;
    margin-bottom: 0;
    padding-top: 2mm;
  }

  .total, .firma {
    border-top: 1px solid black;
    margin-top: 4px;
    padding: 7px 0;
    font-size: 12px;
  }

  .firma {
    padding-top: 10px;
  }

  .lineas-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .lineas {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 3.5px;
    margin-bottom: 0;
  }

  .linea {
    display: flex;
    align-items: center;
    height: 20px;
  }

  .print-only {
    display: block !important;
  }

  .no-print {
    display: none !important;
  }

  .mesa-header {
    border-bottom: 2px solid black;
    padding: 4mm;
    display: flex;
    flex-direction: column;
    height: 24mm;
    margin: 0;
  }

  .header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
  }

  .header-left {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    display: flex;
    gap: 20px;
    align-items: center;
  }

  .mesa-header h1 {
    font-size: 18px;
    font-weight: bold;
    margin: 0;
  }

  .mesa-header h2 {
    font-size: 14px;
    margin: 4px 0 0 0;
  }

  .mesa-info {
    font-size: 14px;
    font-weight: bold;
  }

  .parejas-container {
    margin-top: 0;
    padding: 0;
  }

  .jugadores-grid {
    display: flex;
    justify-content: space-between;
    gap: 0;
    width: 100%;
  }

  .pareja-container {
    width: 50%;
    border: 2px solid black;
    padding: 3mm;
    margin: 0;
    height: 19mm;
  }

  .jugador {
    margin-bottom: 2px;
  }

  .jugador-info {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .nombre {
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 0;
  }

  .puntos-container {
    display: flex;
    gap: 15px;
    margin-left: 15px;
    font-size: 12px;
    margin-top: 1px;
  }

  .numero {
    width: 15px;
    text-align: right;
    margin-right: 5px;
    font-size: 12px;
  }

  .linea-contenido {
    flex: 1;
    border-bottom: 1px solid black;
  }
}
</style> 