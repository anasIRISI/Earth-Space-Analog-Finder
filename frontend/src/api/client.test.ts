import { afterEach, describe, expect, it, vi } from 'vitest'
import { AxiosError, CanceledError } from 'axios'
import { api, probe } from './client'

afterEach(() => vi.restoreAllMocks())

describe('diagnostics API', () => {
  it('retourne la réponse du backend', async () => {
    vi.spyOn(api, 'get').mockResolvedValue({ data: { status: 'ok' } })
    expect(await probe('health/')).toEqual({ data: { status: 'ok' }, error: null })
  })
  it('distingue une indisponibilité PostGIS', async () => {
    const error = new AxiosError('unavailable')
    error.response = { status: 503 } as AxiosError['response']
    vi.spyOn(api, 'get').mockRejectedValue(error)
    expect((await probe('ready/')).error).toContain('PostGIS')
  })
  it('explique une erreur réseau', async () => {
    vi.spyOn(api, 'get').mockRejectedValue(new AxiosError('Network Error'))
    expect((await probe('health/')).error).toContain('CORS')
  })
  it('propage une annulation sans afficher une panne', async () => {
    vi.spyOn(api, 'get').mockRejectedValue(new CanceledError())
    await expect(probe('health/')).rejects.toBeInstanceOf(CanceledError)
  })
})
