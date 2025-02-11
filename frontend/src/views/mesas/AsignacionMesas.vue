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
        <template v-for="(pagina, index) in mesasPorPagina" :key="index" class="print-page">
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
                    <span>Mesa {{ pagina.mesa1.numero }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="parejas-container">
              <div class="jugadores-grid">
                <div class="pareja-container">
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa1.pareja1?.jugador1?.nombre }} {{ pagina.mesa1.pareja1?.jugador1?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa1.pareja1?.jugador1?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa1.pareja1?.jugador1?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa1.pareja1?.jugador2?.nombre }} {{ pagina.mesa1.pareja1?.jugador2?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa1.pareja1?.jugador2?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa1.pareja1?.jugador2?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="pareja-container">
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa1.pareja2?.jugador1?.nombre }} {{ pagina.mesa1.pareja2?.jugador1?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa1.pareja2?.jugador1?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa1.pareja2?.jugador1?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa1.pareja2?.jugador2?.nombre }} {{ pagina.mesa1.pareja2?.jugador2?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa1.pareja2?.jugador2?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa1.pareja2?.jugador2?.PC || 0 }}</span>
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
          <div v-if="pagina.mesa2" class="print-mesa">
            <div class="mesa-header">
              <div class="header-top">
                <div class="header-left">
                  <h1>CAMPEONATO</h1>
                  <h2>Social Club Esportiu Garraf</h2>
                </div>
                <div class="header-right">
                  <div class="mesa-info">
                    <span>Partida {{ partidaActual }}</span>
                    <span>Mesa {{ pagina.mesa2.numero }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="parejas-container">
              <div class="jugadores-grid">
                <div class="pareja-container">
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa2.pareja1?.jugador1?.nombre }} {{ pagina.mesa2.pareja1?.jugador1?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa2.pareja1?.jugador1?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa2.pareja1?.jugador1?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa2.pareja1?.jugador2?.nombre }} {{ pagina.mesa2.pareja1?.jugador2?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa2.pareja1?.jugador2?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa2.pareja1?.jugador2?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="pareja-container">
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa2.pareja2?.jugador1?.nombre }} {{ pagina.mesa2.pareja2?.jugador1?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa2.pareja2?.jugador1?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa2.pareja2?.jugador1?.PC || 0 }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="jugador">
                    <div class="jugador-info">
                      <span class="nombre">{{ pagina.mesa2.pareja2?.jugador2?.nombre }} {{ pagina.mesa2.pareja2?.jugador2?.apellidos }}</span>
                      <div class="puntos-container">
                        <span class="puntos">PG {{ pagina.mesa2.pareja2?.jugador2?.PG || 0 }}</span>
                        <span class="puntos">PC {{ pagina.mesa2.pareja2?.jugador2?.PC || 0 }}</span>
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
    checkCampeonatoSeleccionado()
    if (!campeonatoSeleccionado.value) {
      console.error('No hay campeonato seleccionado')
      return
    }

    const partida = campeonatoSeleccionado.value.partida_actual || 1
    if (typeof partida !== 'number') {
      console.error('La partida actual no es válida:', partida)
      return
    }

    partidaActual.value = partida

    // Obtener las parejas de la partida actual
    const parejasResponse = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partida}`)
    if (!parejasResponse.ok) {
      console.error('Error al cargar las parejas:', parejasResponse.statusText)
      parejas.value = []
      return
    }
    const parejasData = await parejasResponse.json()

    // Asignar los puntos iniciales a cada jugador
    parejas.value = parejasData.map(pareja => ({
      ...pareja,
      jugador1: {
        ...pareja.jugador1,
        PG: pareja.jugador1?.PP || 150,
        PC: pareja.jugador1?.PC || 0
      },
      jugador2: {
        ...pareja.jugador2,
        PG: pareja.jugador2?.PP || 150,
        PC: pareja.jugador2?.PC || 0
      }
    }))

    if (jugadoresOrdenados.value.length > jugadoresPorPagina) {
      iniciarPaginacionAutomatica()
    }
  } catch (error) {
    console.error('Error al cargar los datos:', error)
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
        numero: parseInt(pareja.mesa),
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
  return mesasCompletas.sort((a, b) => parseInt(a.numero) - parseInt(b.numero))
})

// Computed para tener las mesas organizadas por páginas
const mesasPorPagina = computed(() => {
  const paginas = []
  for (let i = 0; i < mesasAplanadas.value.length; i += 2) {
    const pagina = {
      mesa1: mesasAplanadas.value[i],
      mesa2: i + 1 < mesasAplanadas.value.length ? mesasAplanadas.value[i + 1] : null
    }
    paginas.push(pagina)
  }
  return paginas
})

const cargarMesas = async () => {
  try {
    console.log('Cargando mesas para partida:', partidaActual.value)
    const response = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (response.ok) {
      const parejas = await response.json()
      console.log('Parejas recibidas:', parejas)
      
      // Obtener el ranking actualizado
      const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
      if (!rankingResponse.ok) {
        throw new Error('Error al obtener el ranking')
      }
      const rankingData = await rankingResponse.json()
      
      // Crear un mapa para acceso rápido a los datos del ranking
      const rankingMap = new Map(rankingData.map(r => [r.jugador_id, r]))
      
      // Agrupar parejas por mesa
      const mesasTemp = []
      const mesasProcesadas = new Set()
      
      parejas.forEach(pareja => {
        if (!mesasProcesadas.has(pareja.mesa)) {
          const pareja1 = parejas.find(p => p.mesa === pareja.mesa && p.numero_pareja === 1)
          const pareja2 = parejas.find(p => p.mesa === pareja.mesa && p.numero_pareja === 2)
          
          if (pareja1 && pareja2) {
            // Añadir datos del ranking a los jugadores
            if (pareja1.jugador1) {
              const rankingJugador1 = rankingMap.get(pareja1.jugador1_id)
              pareja1.jugador1.PG = rankingJugador1?.PG || 0
              pareja1.jugador1.PC = rankingJugador1?.PC || 0
            }
            if (pareja1.jugador2) {
              const rankingJugador2 = rankingMap.get(pareja1.jugador2_id)
              pareja1.jugador2.PG = rankingJugador2?.PG || 0
              pareja1.jugador2.PC = rankingJugador2?.PC || 0
            }
            if (pareja2.jugador1) {
              const rankingJugador3 = rankingMap.get(pareja2.jugador1_id)
              pareja2.jugador1.PG = rankingJugador3?.PG || 0
              pareja2.jugador1.PC = rankingJugador3?.PC || 0
            }
            if (pareja2.jugador2) {
              const rankingJugador4 = rankingMap.get(pareja2.jugador2_id)
              pareja2.jugador2.PG = rankingJugador4?.PG || 0
              pareja2.jugador2.PC = rankingJugador4?.PC || 0
            }
            
            mesasTemp.push({
              numeroMesa: pareja.mesa,
              pareja1,
              pareja2
            })
            mesasProcesadas.add(pareja.mesa)
          }
        }
      })
      
      console.log('Mesas procesadas:', mesasTemp)
      parejas.value = mesasTemp
      await verificarMesasRegistradas()
    } else {
      console.error('Error al cargar las mesas:', response.statusText)
      parejas.value = []
    }
  } catch (error) {
    console.error('Error al cargar las mesas:', error)
    parejas.value = []
  }
}

const imprimirMesas = async () => {
  try {
    // Obtener el ranking actualizado
    const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
    if (!rankingResponse.ok) {
      throw new Error('Error al obtener el ranking')
    }
    const rankingData = await rankingResponse.json()
    
    // Actualizar los datos de PG y PC de cada jugador
    const rankingMap = new Map(rankingData.map(r => [r.jugador_id, r]))
    
    // Actualizar los datos en las mesas
    mesasAplanadas.value.forEach(mesa => {
      if (mesa.pareja1?.jugador1) {
        const ranking = rankingMap.get(mesa.pareja1.jugador1_id)
        mesa.pareja1.jugador1.PG = ranking?.PG || 0
        mesa.pareja1.jugador1.PC = ranking?.PC || 0
      }
      if (mesa.pareja1?.jugador2) {
        const ranking = rankingMap.get(mesa.pareja1.jugador2_id)
        mesa.pareja1.jugador2.PG = ranking?.PG || 0
        mesa.pareja1.jugador2.PC = ranking?.PC || 0
      }
      if (mesa.pareja2?.jugador1) {
        const ranking = rankingMap.get(mesa.pareja2.jugador1_id)
        mesa.pareja2.jugador1.PG = ranking?.PG || 0
        mesa.pareja2.jugador1.PC = ranking?.PC || 0
      }
      if (mesa.pareja2?.jugador2) {
        const ranking = rankingMap.get(mesa.pareja2.jugador2_id)
        mesa.pareja2.jugador2.PG = ranking?.PG || 0
        mesa.pareja2.jugador2.PC = ranking?.PC || 0
      }
    })
    
    // Forzar una actualización de la vista
    mesasAplanadas.value = [...mesasAplanadas.value]
    
    // Imprimir después de un pequeño delay para asegurar que los datos se han actualizado
    setTimeout(() => {
      window.print()
    }, 100)
  } catch (error) {
    console.error('Error al obtener el ranking:', error)
    alert('Error al obtener los datos del ranking')
  }
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
    margin-bottom: 4px;
  }

  .jugador-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nombre {
    font-weight: bold;
    font-size: 14px;
    margin-right: 10px;
  }

  .puntos-container {
    display: flex;
    gap: 15px;
    margin-left: auto;
    font-size: 12px;
    justify-content: flex-end;
    width: 140px;
  }

  .puntos {
    font-weight: bold;
    color: #333;
    min-width: 50px;
    text-align: right;
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