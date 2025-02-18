<template>
  <div class="imprimir-mesas">
    <ImpresionMesas 
      :mesas-por-pagina="mesasPorPagina"
      :partida-actual="partidaActual"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ImpresionMesas from '@/components/ImpresionMesas.vue'

const route = useRoute()
const router = useRouter()
const campeonatoId = route.params.campeonatoId
const parejas = ref([])
const campeonatoSeleccionado = ref(null)
const partidaActual = ref(0)

const checkCampeonatoSeleccionado = () => {
  const campeonatoGuardado = localStorage.getItem('campeonatoSeleccionado')
  if (campeonatoGuardado) {
    campeonatoSeleccionado.value = JSON.parse(campeonatoGuardado)
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 0
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
      const parejasData = await response.json()
      console.log('Parejas recibidas:', parejasData)
      
      // Obtener el ranking actualizado
      const rankingResponse = await fetch(`http://localhost:8000/api/resultados/ranking/campeonato/${campeonatoId}`)
      if (!rankingResponse.ok) {
        throw new Error('Error al obtener el ranking')
      }
      const rankingData = await rankingResponse.json()
      
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
        jugador2: {
          ...pareja.jugador2,
          PG: rankingMap.get(pareja.jugador2_id)?.PG || 0,
          PC: rankingMap.get(pareja.jugador2_id)?.PC || 0,
          posicion: rankingData.findIndex(r => r.jugador_id === pareja.jugador2_id) + 1
        }
      }))
      
      // Imprimir automáticamente después de cargar los datos
      setTimeout(() => {
        window.print()
      }, 100)
    }
  } catch (error) {
    console.error('Error al cargar las mesas:', error)
    parejas.value = []
  }
}

const handleAfterPrint = () => {
  // Navegar a la vista de registro de resultados
  router.push(`/mesas/registro/${campeonatoId}`)
}

onMounted(() => {
  checkCampeonatoSeleccionado()
  if (campeonatoSeleccionado.value) {
    partidaActual.value = campeonatoSeleccionado.value.partida_actual || 0
  }
  cargarMesas()
  
  // Agregar el evento afterprint
  window.addEventListener('afterprint', handleAfterPrint)
})

onUnmounted(() => {
  // Remover el evento afterprint
  window.removeEventListener('afterprint', handleAfterPrint)
})
</script>

<style scoped>
.imprimir-mesas {
  width: 100%;
  min-height: 100vh;
}

@media screen {
  .imprimir-mesas {
    display: none;
  }
}
</style> 