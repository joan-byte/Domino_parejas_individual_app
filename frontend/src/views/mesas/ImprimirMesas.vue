<template>
  <div class="imprimir-mesas print-only">
    <template v-for="(pagina, index) in mesasPorPagina" :key="index">
      <div class="print-container">
        <div class="mesas-grid">
          <!-- Primera mesa de la página -->
          <div class="print-mesa">
            <div class="mesa-header">
              <div class="header-content">
                <div class="header-left">
                  <h1>CAMPEONATO</h1>
                  <h2>{{ campeonatoSeleccionado?.nombre }}</h2>
                </div>
                <div class="header-right">
                  Partida {{ partidaActual }}Mesa {{ pagina[0]?.numero }}
                </div>
              </div>
            </div>
            
            <!-- Contenido de la primera mesa -->
            <div class="mesa-content">
              <!-- Lado izquierdo -->
              <div class="lado-mesa">
                <div class="jugadores-info">
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[0]?.pareja1?.jugador1?.nombre }} {{ pagina[0]?.pareja1?.jugador1?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[0]?.pareja1?.jugador1?.posicion || '-' }}</span>
                      <span>PG {{ pagina[0]?.pareja1?.jugador1?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[0]?.pareja1?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[0]?.pareja1?.jugador2?.nombre }} {{ pagina[0]?.pareja1?.jugador2?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[0]?.pareja1?.jugador2?.posicion || '-' }}</span>
                      <span>PG {{ pagina[0]?.pareja1?.jugador2?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[0]?.pareja1?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="linea-blanca"></div>
                <div class="puntuacion">
                  <template v-for="n in 15" :key="n">
                    <div class="linea-puntuacion">
                      <span class="numero">{{ n }}</span>
                      <div class="linea">
                        <div class="linea-vertical"></div>
                      </div>
                    </div>
                  </template>
                  <div class="total">Total</div>
                  <div class="firma">Firma</div>
                </div>
              </div>

              <!-- Lado derecho -->
              <div class="lado-mesa">
                <div class="jugadores-info">
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[0]?.pareja2?.jugador1?.nombre }} {{ pagina[0]?.pareja2?.jugador1?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[0]?.pareja2?.jugador1?.posicion || '-' }}</span>
                      <span>PG {{ pagina[0]?.pareja2?.jugador1?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[0]?.pareja2?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[0]?.pareja2?.jugador2?.nombre }} {{ pagina[0]?.pareja2?.jugador2?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[0]?.pareja2?.jugador2?.posicion || '-' }}</span>
                      <span>PG {{ pagina[0]?.pareja2?.jugador2?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[0]?.pareja2?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="linea-blanca"></div>
                <div class="puntuacion">
                  <template v-for="n in 15" :key="n">
                    <div class="linea-puntuacion">
                      <span class="numero">{{ n }}</span>
                      <div class="linea">
                        <div class="linea-vertical"></div>
                      </div>
                    </div>
                  </template>
                  <div class="total">Total</div>
                  <div class="firma">Firma</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Segunda mesa de la página -->
          <div v-if="pagina[1]" class="print-mesa">
            <div class="mesa-header">
              <div class="header-content">
                <div class="header-left">
                  <h1>CAMPEONATO</h1>
                  <h2>{{ campeonatoSeleccionado?.nombre }}</h2>
                </div>
                <div class="header-right">
                  Partida {{ partidaActual }}Mesa {{ pagina[1]?.numero }}
                </div>
              </div>
            </div>
            
            <!-- Contenido de la segunda mesa -->
            <div class="mesa-content">
              <!-- Lado izquierdo -->
              <div class="lado-mesa">
                <div class="jugadores-info">
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[1]?.pareja1?.jugador1?.nombre }} {{ pagina[1]?.pareja1?.jugador1?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[1]?.pareja1?.jugador1?.posicion || '-' }}</span>
                      <span>PG {{ pagina[1]?.pareja1?.jugador1?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[1]?.pareja1?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[1]?.pareja1?.jugador2?.nombre }} {{ pagina[1]?.pareja1?.jugador2?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[1]?.pareja1?.jugador2?.posicion || '-' }}</span>
                      <span>PG {{ pagina[1]?.pareja1?.jugador2?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[1]?.pareja1?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="linea-blanca"></div>
                <div class="puntuacion">
                  <template v-for="n in 15" :key="n">
                    <div class="linea-puntuacion">
                      <span class="numero">{{ n }}</span>
                      <div class="linea">
                        <div class="linea-vertical"></div>
                      </div>
                    </div>
                  </template>
                  <div class="total">Total</div>
                  <div class="firma">Firma</div>
                </div>
              </div>

              <!-- Lado derecho -->
              <div class="lado-mesa">
                <div class="jugadores-info">
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[1]?.pareja2?.jugador1?.nombre }} {{ pagina[1]?.pareja2?.jugador1?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[1]?.pareja2?.jugador1?.posicion || '-' }}</span>
                      <span>PG {{ pagina[1]?.pareja2?.jugador1?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[1]?.pareja2?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                  <div class="jugador-info">
                    <div class="jugador-nombre">
                      {{ pagina[1]?.pareja2?.jugador2?.nombre }} {{ pagina[1]?.pareja2?.jugador2?.apellidos }}
                    </div>
                    <div class="jugador-stats">
                      <span class="pos-stat">Pos. {{ pagina[1]?.pareja2?.jugador2?.posicion || '-' }}</span>
                      <span>PG {{ pagina[1]?.pareja2?.jugador2?.PG || 0 }}</span>
                      <span class="dif-stat">Dif {{ pagina[1]?.pareja2?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="linea-blanca"></div>
                <div class="puntuacion">
                  <template v-for="n in 15" :key="n">
                    <div class="linea-puntuacion">
                      <span class="numero">{{ n }}</span>
                      <div class="linea">
                        <div class="linea-vertical"></div>
                      </div>
                    </div>
                  </template>
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
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(0)
const cargando = ref(true)
const error = ref(false)
const mensajeError = ref('No hay datos disponibles para imprimir.')
const mensajeCarga = ref('Inicializando...')

// Función para cargar la información del campeonato
const cargarInfoCampeonato = async () => {
  mensajeCarga.value = `Cargando información del campeonato ${campeonatoId}...`
  try {
    if (!campeonatoId) {
      throw new Error('ID de campeonato no válido')
    }
    
    console.log('Intentando cargar campeonato con ID:', campeonatoId)
    const response = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!response.ok) {
      throw new Error(`Error al obtener campeonato: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('Datos del campeonato recibidos:', data)
    campeonatoSeleccionado.value = data
    partidaActual.value = data.partida_actual || 0
    
    // Forzar la actualización del nombre del campeonato
    if (data.nombre) {
      console.log('Nombre del campeonato:', data.nombre)
      campeonatoSeleccionado.value = { ...data }
    }
    
    return data
  } catch (error) {
    console.error('Error al cargar información del campeonato:', error)
    throw error
  }
}

// Verificar el campeonato seleccionado en localStorage
const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    try {
      const campeonato = JSON.parse(campeonatoGuardado)
      console.log('Campeonato encontrado en localStorage:', campeonato)
      campeonatoSeleccionado.value = campeonato
      partidaActual.value = campeonato.partida_actual || 0
    } catch (error) {
      console.error('Error al parsear campeonato de localStorage:', error)
    }
  }
}

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
      mesaActual.pareja1 = {
        ...pareja,
        jugador1: {
          ...pareja.jugador1,
          PG: pareja.jugador1?.PG || 0,
          PC: pareja.jugador1?.PC || 0,
          posicion: pareja.jugador1?.posicion || '-'
        },
        jugador2: {
          ...pareja.jugador2,
          PG: pareja.jugador2?.PG || 0,
          PC: pareja.jugador2?.PC || 0,
          posicion: pareja.jugador2?.posicion || '-'
        }
      }
    } else if (pareja.numero_pareja === 2) {
      mesaActual.pareja2 = {
        ...pareja,
        jugador1: {
          ...pareja.jugador1,
          PG: pareja.jugador1?.PG || 0,
          PC: pareja.jugador1?.PC || 0,
          posicion: pareja.jugador1?.posicion || '-'
        },
        jugador2: {
          ...pareja.jugador2,
          PG: pareja.jugador2?.PG || 0,
          PC: pareja.jugador2?.PC || 0,
          posicion: pareja.jugador2?.posicion || '-'
        }
      }
    }
  })

  // Convertir el Map a array y filtrar mesas completas
  const mesasCompletas = Array.from(mesasMap.values())
    .filter(mesa => mesa.pareja1 && mesa.pareja2)
    .sort((a, b) => parseInt(a.numero) - parseInt(b.numero))

  console.log('Mesas completas:', mesasCompletas)
  return mesasCompletas
})

// Computed para tener las mesas organizadas por páginas
const mesasPorPagina = computed(() => {
  const paginas = []
  const mesas = mesasAplanadas.value
  
  for (let i = 0; i < mesas.length; i += 2) {
    const pagina = []
    // Agregar primera mesa
    pagina.push(mesas[i])
    // Agregar segunda mesa si existe
    if (i + 1 < mesas.length) {
      pagina.push(mesas[i + 1])
    }
    paginas.push(pagina)
  }
  
  console.log('Páginas generadas:', paginas)
  return paginas
})

// Cargar los datos de las mesas y el ranking
const cargarMesas = async () => {
  try {
    mensajeCarga.value = 'Cargando datos de mesas y ranking...'
    console.log('Cargando mesas para partida:', partidaActual.value)
    
    // Obtener las parejas
    const response = await fetch(`http://localhost:8000/api/parejas-partida/campeonato/${campeonatoId}/partida/${partidaActual.value}`)
    if (!response.ok) {
      throw new Error('Error al cargar las parejas')
    }
    
    const parejasData = await response.json()
    console.log('Parejas recibidas:', parejasData.length)
    
    // Obtener el ranking actualizado
    const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
    if (!rankingResponse.ok) {
      throw new Error('Error al obtener el ranking')
    }
    
    const rankingData = await rankingResponse.json()
    console.log('Datos del ranking:', rankingData)
    
    // Crear un mapa para acceso rápido a los datos del ranking
    const rankingMap = new Map(rankingData.map(r => [r.jugador_id, r]))
    
    // Actualizar los datos de las parejas con la información del ranking
    parejas.value = parejasData.map(pareja => ({
      ...pareja,
      jugador1: {
        ...pareja.jugador1,
        PG: rankingMap.get(pareja.jugador1_id)?.PG || 0,
        PC: rankingMap.get(pareja.jugador1_id)?.PC || 0,
        posicion: rankingData.findIndex(r => r.jugador_id === pareja.jugador1_id) + 1
      },
      jugador2: pareja.jugador2 ? {
        ...pareja.jugador2,
        PG: rankingMap.get(pareja.jugador2_id)?.PG || 0,
        PC: rankingMap.get(pareja.jugador2_id)?.PC || 0,
        posicion: rankingData.findIndex(r => r.jugador_id === pareja.jugador2_id) + 1
      } : null
    }))
    
    cargando.value = false
    error.value = false
    
    // Esperar a que Vue actualice el DOM antes de imprimir
    await nextTick()
    
    // Verificar que tenemos datos antes de imprimir
    if (mesasPorPagina.value.length > 0) {
      console.log('Preparando impresión con', mesasPorPagina.value.length, 'páginas')
      setTimeout(() => {
        window.print()
      }, 1000) // Aumentar el tiempo de espera para asegurar que todo esté listo
    } else {
      throw new Error('No hay mesas para imprimir')
    }
  } catch (error) {
    console.error('Error al cargar las mesas:', error)
    mensajeError.value = error.message || 'Error al cargar los datos para impresión'
    error.value = true
    cargando.value = false
    parejas.value = []
  }
}

// Función para reintentar la carga de datos
const reintentar = () => {
  error.value = false
  cargando.value = true
  inicializarDatos()
}

// Función para inicializar los datos
const inicializarDatos = async () => {
  cargando.value = true
  error.value = false
  
  try {
    // Cargar información del campeonato
    await cargarInfoCampeonato()
    
    // Cargar parejas y ranking
    await cargarMesas()
  } catch (error) {
    console.error('Error en inicializarDatos:', error)
    mensajeError.value = error.message || 'Error al cargar los datos para impresión'
    error.value = true
    cargando.value = false
  }
}

// Manejar el evento después de imprimir
const handleAfterPrint = () => {
  // Navegar a la vista de registro de resultados
  router.push(`/mesas/registro/${campeonatoId}`)
}

onMounted(() => {
  inicializarDatos()
  // Agregar el evento afterprint
  window.addEventListener('afterprint', handleAfterPrint)
  console.log('Componente ImprimirMesas montado')
})

onUnmounted(() => {
  // Remover el evento afterprint
  window.removeEventListener('afterprint', handleAfterPrint)
})
</script>

<style scoped>
/* Estilos para la impresión */
@media print {
  @page {
    size: A4 landscape !important;
    margin: 0 !important;
  }

  html {
    width: 297mm !important;
    height: 210mm !important;
    overflow: hidden !important;
  }

  body {
    width: 297mm !important;
    height: 210mm !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
  }

  .imprimir-mesas {
    width: 297mm !important;
    height: 210mm !important;
    margin: 0 !important;
    padding: 0 !important;
    background: white !important;
    transform-origin: top left !important;
    transform: rotate(0deg) !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
  }

  .print-container {
    width: 297mm !important;
    height: 210mm !important;
    padding: 5mm !important;
    box-sizing: border-box !important;
    page-break-after: avoid !important;
    page-break-inside: avoid !important;
    display: flex !important;
    flex-direction: row !important;
  }

  .mesas-grid {
    display: grid;
    grid-template-columns: repeat(2, calc(50% - 2.5mm));
    gap: 5mm;
    width: 100%;
    height: 100%;
  }

  .print-mesa {
    border: 2px solid black;
    background: white;
    page-break-inside: avoid;
    height: 200mm;
  }

  .mesa-header {
    border-bottom: 2px solid black;
    padding: 4mm;
    background-color: #f5f5f5;
    height: 20mm;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
  }

  .header-left h1 {
    font-size: 18pt;
    margin: 0;
    font-weight: bold;
  }

  .header-left h2 {
    font-size: 16pt;
    margin: 2mm 0 0;
  }

  .header-right {
    text-align: right;
    font-size: 14pt;
    font-weight: bold;
  }

  .mesa-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: calc(100% - 20mm);
    border: 2px solid black;
  }

  .lado-mesa {
    padding: 5mm;
    border-right: 2px solid black;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .lado-mesa:last-child {
    border-right: none;
  }

  .jugadores-info {
    margin-bottom: 5mm;
    border: 2px solid black;
    padding: 6mm;
    border-radius: 2mm;
    background-color: white;
    height: fit-content;
    width: 100%;
    box-sizing: border-box;
  }

  .jugador-info {
    margin-bottom: 3mm;
    padding: 2mm;
    width: 100%;
  }

  .jugador-info:last-child {
    margin-bottom: 0;
  }

  .jugador-nombre {
    font-size: 12pt;
    font-weight: bold;
    margin-bottom: 3mm;
    text-align: center;
    width: 100%;
  }

  .jugador-stats {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 2mm;
    padding: 0;
    font-size: 11pt;
    width: 100%;
  }

  .jugador-stats span {
    padding: 1.5mm;
    background-color: #f5f5f5;
    border-radius: 1.5mm;
    border: 1px solid #ddd;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 0;
  }

  .pos-stat {
    justify-self: start;
  }

  .dif-stat {
    justify-self: end;
  }

  .linea-blanca {
    height: 5mm;
  }

  .puntuacion {
    border: 2px solid black;
    padding: 3mm;
    border-radius: 2mm;
    background-color: white;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
  }

  .total {
    border: 2px solid black;
    padding: 2mm 4mm;
    font-size: 11pt;
    font-weight: bold;
    height: 8mm;
    background-color: #f5f5f5;
    border-radius: 2mm;
    text-align: left;
    margin-top: 3mm;
  }

  .firma {
    border: 2px solid black;
    padding: 2mm 4mm;
    font-size: 11pt;
    font-weight: bold;
    height: 20mm;
    background-color: #f5f5f5;
    border-radius: 2mm;
    text-align: left;
    position: absolute;
    bottom: 3mm;
    left: 3mm;
    right: 3mm;
  }

  .linea-puntuacion:last-child {
    margin-bottom: 34mm; /* Espacio para Total y Firma */
  }

  .linea-puntuacion {
    display: flex;
    align-items: center;
    gap: 2mm;
    height: 7mm;
    border-bottom: 1px solid #999;
    position: relative;
  }

  .linea-puntuacion .numero {
    width: 4mm;
    text-align: right;
    font-size: 10pt;
    font-weight: bold;
  }

  .linea-puntuacion .linea {
    flex: 1;
    border: 1px solid #666;
    height: 5mm;
    position: relative;
    background-color: #fff;
  }

  .linea-vertical {
    position: absolute;
    left: 50%;
    height: 100%;
    width: 1px;
    background-color: black;
    border-left: 1px solid black;
  }
}

/* Estilos para la vista en pantalla */
@media screen {
  .print-only {
    display: none;
  }
}
</style> 