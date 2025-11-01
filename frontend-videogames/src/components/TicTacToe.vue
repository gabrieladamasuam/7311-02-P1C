<template>
  <div class="tictactoe">
    <h2>Tres en Raya</h2>
    <p class="status">
      <template v-if="!winner">
        Turno: {{ xIsNext ? 'X' : 'O' }}
      </template>
      <template v-else>
        <span v-if="winner !== 'Empate'">Ganador: {{ winner }}</span>
        <span v-else>¡Empate!</span>
      </template>
    </p>
    <div class="board">
      <button
        v-for="(cell, i) in board"
        :key="i"
        type="button"
        @click="makeMove(i)"
        :disabled="!!cell || !!winner"
        :class="{ 'cell-x': cell === 'X', 'cell-o': cell === 'O' }"
      >
        {{ cell }}
      </button>
    </div>
    <div class="result">
      <button class="reset" type="button" @click="reset">Reiniciar</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import JSConfetti from 'js-confetti'
const confetti = new JSConfetti()

const board = ref(Array(9).fill(''))
const xIsNext = ref(true)
const winner = ref('')

function makeMove(i) {
  if (board.value[i] || winner.value) return
  board.value[i] = xIsNext.value ? 'X' : 'O'
  xIsNext.value = !xIsNext.value
  checkWinner()
}

function showConfetti() {
  confetti.addConfetti()
}

function checkWinner() {
  const lines = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
  ]
  for (const [a,b,c] of lines) {
    if (board.value[a] && board.value[a] === board.value[b] && board.value[a] === board.value[c]) {
      winner.value = board.value[a]
      showConfetti(winner.value)
      return
    }
  }
  if (board.value.every(cell => cell)) {
    winner.value = 'Empate'
  }
}

function reset() {
  board.value = Array(9).fill('')
  xIsNext.value = true
  winner.value = ''
}
</script>