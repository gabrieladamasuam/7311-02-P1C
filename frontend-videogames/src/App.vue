<script setup>
import { ref, computed } from 'vue'
import GamePanel from './components/GamePanel.vue'
import TicTacToe from './components/TicTacToe.vue'

const currentViewName = ref('')

// Convierte el nombre en componente
const activeComponent = computed(() => {
  if (currentViewName.value === 'TicTacToe') return TicTacToe
  return null
})

function handlePlay(game) {
  currentViewName.value = game.playableComponent || ''
}

function exitGame() {
  currentViewName.value = ''
}
</script>

<template>
  <main>
    <h1>Portal de Juegos</h1>

    <template v-if="!activeComponent">
      <GamePanel @play="handlePlay" />
    </template>

    <template v-else>
      <div class="game-container">
  <button type="button" class="back-btn btn" @click="exitGame">Volver</button>
        <keep-alive>
          <component :is="activeComponent" />
        </keep-alive>
      </div>
    </template>
  </main>
</template>