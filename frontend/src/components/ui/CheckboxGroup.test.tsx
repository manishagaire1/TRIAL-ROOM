import { useState } from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CheckboxGroup } from './CheckboxGroup'

// CheckboxGroup is a controlled component (state lives in the parent),
// so the test needs a small stateful wrapper to exercise real toggling —
// this is exactly how every page in the app actually uses it.
function ControlledCheckboxGroup() {
  const [value, setValue] = useState<string[]>(['Black'])
  return (
    <CheckboxGroup label="Favorite colors" options={['Black', 'White', 'Navy']} value={value} onChange={setValue} />
  )
}

describe('CheckboxGroup', () => {
  it('renders every option and reflects initial selection', () => {
    render(<ControlledCheckboxGroup />)
    expect(screen.getByRole('button', { name: 'Black' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'White' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('selects an unselected option on click', async () => {
    const user = userEvent.setup()
    render(<ControlledCheckboxGroup />)

    await user.click(screen.getByRole('button', { name: 'Navy' }))

    expect(screen.getByRole('button', { name: 'Navy' })).toHaveAttribute('aria-pressed', 'true')
    // Existing selection is preserved, not replaced.
    expect(screen.getByRole('button', { name: 'Black' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('deselects an already-selected option on click', async () => {
    const user = userEvent.setup()
    render(<ControlledCheckboxGroup />)

    await user.click(screen.getByRole('button', { name: 'Black' }))

    expect(screen.getByRole('button', { name: 'Black' })).toHaveAttribute('aria-pressed', 'false')
  })
})
