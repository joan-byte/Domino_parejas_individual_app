<template>
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
                      <span class="puntos">Pos {{ pagina.mesa1.pareja1?.jugador1?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa1.pareja1?.jugador1?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa1.pareja1?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa1.pareja1?.jugador2?.nombre }} {{ pagina.mesa1.pareja1?.jugador2?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa1.pareja1?.jugador2?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa1.pareja1?.jugador2?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa1.pareja1?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="pareja-container">
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa1.pareja2?.jugador1?.nombre }} {{ pagina.mesa1.pareja2?.jugador1?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa1.pareja2?.jugador1?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa1.pareja2?.jugador1?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa1.pareja2?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa1.pareja2?.jugador2?.nombre }} {{ pagina.mesa1.pareja2?.jugador2?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa1.pareja2?.jugador2?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa1.pareja2?.jugador2?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa1.pareja2?.jugador2?.PC || 0 }}</span>
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
                      <span class="puntos">Pos {{ pagina.mesa2.pareja1?.jugador1?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa2.pareja1?.jugador1?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa2.pareja1?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa2.pareja1?.jugador2?.nombre }} {{ pagina.mesa2.pareja1?.jugador2?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa2.pareja1?.jugador2?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa2.pareja1?.jugador2?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa2.pareja1?.jugador2?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="pareja-container">
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa2.pareja2?.jugador1?.nombre }} {{ pagina.mesa2.pareja2?.jugador1?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa2.pareja2?.jugador1?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa2.pareja2?.jugador1?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa2.pareja2?.jugador1?.PC || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="jugador">
                  <div class="jugador-info">
                    <span class="nombre">{{ pagina.mesa2.pareja2?.jugador2?.nombre }} {{ pagina.mesa2.pareja2?.jugador2?.apellidos }}</span>
                    <div class="puntos-container">
                      <span class="puntos">Pos {{ pagina.mesa2.pareja2?.jugador2?.posicion || '-' }}</span>
                      <span class="puntos">PG {{ pagina.mesa2.pareja2?.jugador2?.PG || 0 }}</span>
                      <span class="puntos">Dif. {{ pagina.mesa2.pareja2?.jugador2?.PC || 0 }}</span>
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
</template>

<script setup>
import { defineProps } from 'vue'

// Definir las props que recibirá el componente
const props = defineProps({
  mesasPorPagina: {
    type: Array,
    required: true
  },
  partidaActual: {
    type: Number,
    required: true
  }
})
</script>

<style scoped>
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
    display: flex;
    gap: 15px;
  }

  .mesa-info span {
    white-space: nowrap;
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
    gap: 10px;
    margin-left: auto;
    font-size: 12px;
    justify-content: flex-end;
    width: 180px;
  }

  .puntos {
    font-weight: bold;
    color: #333;
    min-width: 45px;
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