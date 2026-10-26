import { useEffect, useState } from 'react'
import { probe, type Health, type ProbeResult, type Readiness } from '../api/client'

export function useDiagnostics() {
  const [request, setRequest] = useState(0)
  const [loading, setLoading] = useState(true)
  const [checkedAt, setCheckedAt] = useState<Date | null>(null)
  const [health, setHealth] = useState<ProbeResult<Health>>({ data: null, error: null })
  const [readiness, setReadiness] = useState<ProbeResult<Readiness>>({ data: null, error: null })

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    Promise.all([
      probe<Health>('health/', controller.signal),
      probe<Readiness>('ready/', controller.signal),
    ]).then(([apiHealth, databaseHealth]) => {
      if (controller.signal.aborted) return
      setHealth(apiHealth)
      setReadiness(databaseHealth)
      setCheckedAt(new Date())
      setLoading(false)
    }).catch(() => {
      // L'annulation au démontage (ou en StrictMode) ne représente pas une panne.
      if (!controller.signal.aborted) setLoading(false)
    })
    return () => controller.abort()
  }, [request])

  return { health, readiness, loading, checkedAt, refresh: () => setRequest((value) => value + 1) }
}
