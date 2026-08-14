interface CheckboxGroupProps {
  label: string
  options: string[]
  value: string[]
  onChange: (value: string[]) => void
}

export function CheckboxGroup({ label, options, value, onChange }: CheckboxGroupProps) {
  const toggle = (option: string) => {
    onChange(
      value.includes(option) ? value.filter((v) => v !== option) : [...value, option],
    )
  }

  return (
    <fieldset>
      <legend className="mb-2 text-sm font-medium text-neutral-700">{label}</legend>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const checked = value.includes(option)
          return (
            <button
              key={option}
              type="button"
              aria-pressed={checked}
              onClick={() => toggle(option)}
              className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                checked
                  ? 'border-neutral-900 bg-neutral-900 text-white'
                  : 'border-neutral-300 text-neutral-700 hover:border-neutral-400'
              }`}
            >
              {option}
            </button>
          )
        })}
      </div>
    </fieldset>
  )
}
