<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'

const testBackend = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/test')
    const data = await response.json()
    console.log('Backend response:', data)
  } catch (error) {
    console.error('Error connecting to backend:', error)
  }
}

onMounted(testBackend)
</script>

<template>
  <header>
    <h1>Domino Parejas Individual</h1>
  </header>

  <RouterView />
</template>

<style>
header {
  padding: 2rem;
  background-color: #f3f4f6;
}

h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
}
</style>
