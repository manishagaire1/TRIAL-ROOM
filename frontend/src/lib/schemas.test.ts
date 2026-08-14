import { loginSchema, registerSchema } from './schemas'

describe('loginSchema', () => {
  it('accepts a valid email and non-empty password', () => {
    const result = loginSchema.safeParse({ email: 'user@example.com', password: 'x' })
    expect(result.success).toBe(true)
  })

  it('rejects an invalid email', () => {
    const result = loginSchema.safeParse({ email: 'not-an-email', password: 'x' })
    expect(result.success).toBe(false)
  })

  it('rejects an empty password', () => {
    const result = loginSchema.safeParse({ email: 'user@example.com', password: '' })
    expect(result.success).toBe(false)
  })
})

describe('registerSchema', () => {
  const base = { email: 'user@example.com', password: 'password123', confirmPassword: 'password123' }

  it('accepts matching passwords of sufficient length', () => {
    expect(registerSchema.safeParse(base).success).toBe(true)
  })

  it('rejects a password under 8 characters', () => {
    const result = registerSchema.safeParse({ ...base, password: 'short', confirmPassword: 'short' })
    expect(result.success).toBe(false)
  })

  it('rejects mismatched passwords and flags confirmPassword specifically', () => {
    const result = registerSchema.safeParse({ ...base, confirmPassword: 'different123' })
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].path).toEqual(['confirmPassword'])
    }
  })
})
