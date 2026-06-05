import { ref, computed, watch } from 'vue'
import type { AlgorithmDef, AlgorithmStep } from '@/data/algorithms'

export function useAlgorithmPlayer() {
  const selectedAlgorithm = ref<AlgorithmDef | null>(null)
  const steps = ref<AlgorithmStep[]>([])
  const currentIndex = ref(0)
  const isPlaying = ref(false)
  const speed = ref(800) // ms per step
  const error = ref<string | null>(null)
  const isRunning = ref(false)
  const inputText = ref('')

  let timer: ReturnType<typeof setInterval> | null = null

  const totalSteps = computed(() => steps.value.length)
  const currentStep = computed(() => steps.value[currentIndex.value] || null)
  const isComplete = computed(() => steps.value.length > 0 && currentIndex.value >= steps.value.length - 1)
  const progress = computed(() => totalSteps.value > 0 ? ((currentIndex.value + 1) / totalSteps.value) * 100 : 0)

  const speedOptions = [
    { value: 400, label: '0.5x' },
    { value: 800, label: '1x' },
    { value: 1500, label: '2x' },
    { value: 3000, label: '3x' },
  ]

  function setInput(text: string) {
    inputText.value = text
  }

  async function runAlgorithm(algo: AlgorithmDef, input: unknown) {
    error.value = null
    isRunning.value = true
    steps.value = []
    currentIndex.value = 0
    pause()

    try {
      // Collect all steps synchronously from the generator
      const gen = algo.generateSteps(input)
      const collected: AlgorithmStep[] = []
      for (const step of gen) {
        collected.push(step)
      }
      steps.value = collected
    } catch (e: any) {
      error.value = e?.message || '算法执行出错'
    } finally {
      isRunning.value = false
    }
  }

  function play() {
    if (isComplete.value) {
      currentIndex.value = 0
    }
    isPlaying.value = true
    timer = setInterval(() => {
      if (currentIndex.value < totalSteps.value - 1) {
        currentIndex.value++
      } else {
        pause()
      }
    }, speed.value)
  }

  function pause() {
    isPlaying.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function togglePlay() {
    isPlaying.value ? pause() : play()
  }

  function stepForward() {
    pause()
    if (currentIndex.value < totalSteps.value - 1) {
      currentIndex.value++
    }
  }

  function stepBack() {
    pause()
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  function reset() {
    pause()
    currentIndex.value = 0
  }

  function setSpeed(ms: number) {
    speed.value = ms
    if (isPlaying.value) {
      pause()
      play()
    }
  }

  // Update timer interval when speed changes
  watch(speed, () => {
    if (isPlaying.value) {
      pause()
      play()
    }
  })

  return {
    selectedAlgorithm,
    steps,
    currentIndex,
    currentStep,
    totalSteps,
    isPlaying,
    isComplete,
    isRunning,
    error,
    speed,
    speedOptions,
    progress,
    inputText,
    setInput,
    runAlgorithm,
    play,
    pause,
    togglePlay,
    stepForward,
    stepBack,
    reset,
    setSpeed,
  }
}
