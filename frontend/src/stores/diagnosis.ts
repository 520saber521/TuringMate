import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DiagnosisReport } from '@/types/diagnosis'

export const useDiagnosisStore = defineStore('diagnosis', () => {
  const report = ref<DiagnosisReport | null>( null)

  function setReport(r: DiagnosisReport) {
    report.value = r
  }

  return { report, setReport }
})
