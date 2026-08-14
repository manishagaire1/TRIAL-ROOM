import { AxiosError } from 'axios'
import { getApiErrorMessage } from './apiError'

function makeAxiosError(data: unknown): AxiosError {
  const error = new AxiosError('Request failed')
  error.response = {
    data,
    status: 400,
    statusText: 'Bad Request',
    headers: {},
    // @ts-expect-error minimal fake config for the test
    config: {},
  }
  return error
}

describe('getApiErrorMessage', () => {
  it('extracts the message from the backend error envelope', () => {
    const error = makeAxiosError({ error: { code: 'BAD_REQUEST', message: 'Size not available.' } })
    expect(getApiErrorMessage(error)).toBe('Size not available.')
  })

  it('falls back to a generic message when the envelope is missing', () => {
    const error = makeAxiosError({ detail: 'unexpected shape' })
    expect(getApiErrorMessage(error)).toBe('Something went wrong. Please try again.')
  })

  it('falls back to a generic message for a non-axios error (e.g. network failure)', () => {
    expect(getApiErrorMessage(new Error('Network Error'))).toBe(
      'Something went wrong. Please try again.',
    )
  })

  it('falls back when the message field is not a string', () => {
    const error = makeAxiosError({ error: { message: 12345 } })
    expect(getApiErrorMessage(error)).toBe('Something went wrong. Please try again.')
  })
})
