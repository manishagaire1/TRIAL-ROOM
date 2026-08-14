import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getStylePreferences, updateStylePreferences } from '../../api/profile'
import { getApiErrorMessage } from '../../lib/apiError'
import { COLOR_GROUPS, FAVORITE_COLORS, OCCASIONS, STYLES } from '../../lib/profileOptions'
import type { StylePreference } from '../../types/user'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { CheckboxGroup } from '../ui/CheckboxGroup'

interface FormValues {
  favorite_colors: string[]
  color_group: string
  styles: string[]
  occasions: string[]
}

export function StylePreferencesForm() {
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)
  const { data, isLoading } = useQuery({
    queryKey: ['style-preferences'],
    queryFn: getStylePreferences,
  })

  const { register, control, handleSubmit, formState } = useForm<FormValues>({
    values: data
      ? {
          favorite_colors: data.favorite_colors,
          color_group: data.color_group ?? '',
          styles: data.styles,
          occasions: data.occasions,
        }
      : undefined,
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      updateStylePreferences({
        favorite_colors: values.favorite_colors,
        color_group:
          (values.color_group || null) as StylePreference['color_group'],
        styles: values.styles,
        occasions: values.occasions,
      }),
    onSuccess: (updated: StylePreference) => {
      queryClient.setQueryData(['style-preferences'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (isLoading) return <Card title="Style preferences">Loading...</Card>

  return (
    <Card title="Style preferences">
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-5"
      >
        <Controller
          name="favorite_colors"
          control={control}
          render={({ field }) => (
            <CheckboxGroup
              label="Favorite colors"
              options={FAVORITE_COLORS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />

        <Controller
          name="styles"
          control={control}
          render={({ field }) => (
            <CheckboxGroup
              label="Style"
              options={STYLES}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />

        <Controller
          name="occasions"
          control={control}
          render={({ field }) => (
            <CheckboxGroup
              label="Occasions"
              options={OCCASIONS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />

        <div className="flex flex-col gap-1">
          <label htmlFor="color_group" className="text-sm font-medium text-neutral-700">
            Preferred color group
          </label>
          <select
            id="color_group"
            {...register('color_group')}
            className="w-48 rounded-md border border-neutral-300 px-3 py-2 text-sm"
          >
            <option value="">Not set</option>
            {COLOR_GROUPS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3">
          <Button type="submit" disabled={formState.isSubmitting}>
            {formState.isSubmitting ? 'Saving...' : 'Save'}
          </Button>
          {saved && <span className="text-sm text-green-600">Saved</span>}
          {mutation.isError && (
            <span className="text-sm text-red-600">
              {getApiErrorMessage(mutation.error)}
            </span>
          )}
        </div>
      </form>
    </Card>
  )
}
