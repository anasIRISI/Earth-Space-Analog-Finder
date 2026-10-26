import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/',
  timeout: 8000,
  headers: { Accept: 'application/json' },
})

export const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://localhost:8000'

export interface Health {
  status: 'ok'
  service: string
  phase: number
  python_version: string
  django_version: string
}

export interface Readiness {
  status: 'ready' | 'unavailable'
  database: string
  postgis_version: string | null
  message: string
}

export interface ProbeResult<T> {
  data: T | null
  error: string | null
}

export async function probe<T>(path: string, signal?: AbortSignal): Promise<ProbeResult<T>> {
  try {
    const response = await api.get<T>(path, { signal })
    return { data: response.data, error: null }
  } catch (error) {
    if (axios.isCancel(error)) throw error
    if (axios.isAxiosError(error) && error.response?.status === 503) {
      return { data: null, error: 'PostgreSQL ou PostGIS indisponible. Vérifiez les conteneurs et les migrations.' }
    }
    return { data: null, error: 'Service inaccessible. Vérifiez le backend, son adresse et la configuration CORS.' }
  }
}
