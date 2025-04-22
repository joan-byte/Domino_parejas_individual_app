<template>
  <div class="print-only">
    <div class="ranking-print">
      <div class="ranking-page" v-for="(pagina, index) in paginas" :key="index">
        <div class="header">
          <h2>Ranking del Campeonato</h2>
          <div class="tournament-info">
            <p>{{ tournamentName }}</p>
            <p>{{ estadoPartida }}</p>
          </div>
        </div>

        <table class="ranking-table">
          <thead>
            <tr>
              <th>Pos.</th>
              <th>Partida</th>
              <th>PG</th>
              <th>Dif.</th>
              <th>PV</th>
              <th>PT</th>
              <th>MG</th>
              <th>ID</th>
              <th>Nombre</th>
              <th>Apellidos</th>
              <th>Club</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(jugador, idx) in pagina" :key="jugador.id">
              <td>{{ calcularPosicion(index, idx) }}</td>
              <td>{{ jugador.ultima_partida }}</td>
              <td>{{ jugador.PG }}</td>
              <td>{{ jugador.PC }}</td>
              <td>{{ jugador.PV }}</td>
              <td>{{ jugador.PT }}</td>
              <td>{{ jugador.MG }}</td>
              <td>{{ jugador.jugador_id }}</td>
              <td>{{ jugador.nombre }}</td>
              <td>{{ jugador.apellidos }}</td>
              <td>{{ jugador.club }}</td>
            </tr>
          </tbody>
        </table>
        
        <div class="footer">
          <p>Página {{ index + 1 }} de {{ paginas.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const campeonatoId = parseInt(route.params.campeonatoId)
const tournamentName = ref('')
const partidaActual = ref(1)
const rankingData = ref([])
const campeonatoFinalizado = ref(false)

// Configuración de paginación - Ajustado para A4 con márgenes
const JUGADORES_POR_PAGINA = 25 // Aumentado para aprovechar mejor el espacio

// Texto del estado de la partida
const estadoPartida = computed(() => {
  return campeonatoFinalizado.value ? 'Clasificación Final' : `Partida: ${partidaActual.value}`
})

// Dividir los datos en páginas de manera óptima
const paginas = computed(() => {
  const paginas = []
  const totalJugadores = rankingData.value.length
  
  for (let i = 0; i < totalJugadores; i += JUGADORES_POR_PAGINA) {
    const paginaActual = rankingData.value.slice(i, Math.min(i + JUGADORES_POR_PAGINA, totalJugadores))
    paginas.push(paginaActual)
  }
  
  return paginas
})

// Calcular la posición real del jugador
const calcularPosicion = (numeroPagina, indiceEnPagina) => {
  return numeroPagina * JUGADORES_POR_PAGINA + indiceEnPagina + 1
}

// Cargar los datos e imprimir
const cargarEImprimir = async () => {
  try {
    // Obtener la información del campeonato
    const campeonatoResponse = await fetch(`http://localhost:8000/api/campeonatos/${campeonatoId}`)
    if (!campeonatoResponse.ok) throw new Error(`Error al obtener el campeonato`)
    const campeonato = await campeonatoResponse.json()
    
    tournamentName.value = campeonato.nombre
    partidaActual.value = campeonato.partida_actual
    campeonatoFinalizado.value = campeonato.finalizado

    // Si el campeonato está finalizado, usamos el número total de partidas
    const partidaParaRanking = campeonato.finalizado ? campeonato.numero_partidas : campeonato.partida_actual
    
    // Obtener el ranking usando la partida correspondiente
    const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}?partida=${partidaParaRanking}`)
    if (!rankingResponse.ok) throw new Error(`Error al obtener ranking`)
    const data = await rankingResponse.json()
    
    if (!Array.isArray(data)) throw new Error('Datos de ranking inválidos')
    rankingData.value = data

    // Esperar a que Vue actualice el DOM
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Imprimir y volver a la página anterior
    if (rankingData.value.length > 0) {
      window.print()
      router.back()
    }
  } catch (error) {
    console.error('Error:', error)
    router.back()
  }
}

onMounted(() => {
  cargarEImprimir()
})
</script>

<style>
/* Estilos para pantalla */
.print-only {
  position: absolute;
  width: 210mm;
  margin: 0 auto;
  background: white;
  left: 50%;
  transform: translateX(-50%);
  padding: 20px;
}

.ranking-print {
  background: white;
}

.ranking-page {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #ddd;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.tournament-info {
  margin: 10px 0;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.ranking-table th,
.ranking-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.ranking-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.footer {
  text-align: center;
  margin-top: 20px;
  font-size: 12px;
}

/* Estilos específicos para impresión */
@media print {
  @page {
    size: A4 portrait;
    margin: 2cm 1.5cm; /* Márgenes uniformes */
  }

  body {
    background: white;
    margin: 0;
    padding: 0;
  }

  .print-only {
    position: static;
    width: 100%;
    transform: none;
    padding: 0;
    margin: 0;
  }

  .ranking-page {
    page-break-after: always;
    border: none;
    padding: 0;
    margin: 0;
    height: calc(100vh - 4cm); /* Altura total menos márgenes */
    display: flex;
    flex-direction: column;
  }

  .ranking-page:last-child {
    page-break-after: avoid;
  }

  .header {
    margin-bottom: 1cm;
    position: relative;
    flex-shrink: 0;
  }

  .ranking-table {
    width: 100%;
    margin: 0;
    border-collapse: collapse;
    flex: 1;
  }

  .ranking-table thead {
    display: table-header-group; /* Repetir encabezados en cada página */
  }

  .ranking-table th {
    background-color: #f0f0f0 !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    padding: 0.3cm;
    font-weight: bold;
    border: 1px solid #000;
  }

  .ranking-table td {
    padding: 0.2cm;
    border: 1px solid #000;
  }

  .footer {
    margin-top: 1cm;
    position: relative;
    flex-shrink: 0;
  }

  /* Ajustar tamaños de texto para impresión */
  .header h2 {
    font-size: 18pt;
    margin: 0 0 0.5cm 0;
  }

  .tournament-info p {
    font-size: 14pt;
    margin: 0.2cm 0;
  }

  .ranking-table th,
  .ranking-table td {
    font-size: 11pt;
  }

  .footer p {
    font-size: 10pt;
  }
}
</style> 