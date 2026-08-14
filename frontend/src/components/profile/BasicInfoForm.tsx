import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getProfile, updateProfile } from '../../api/profile'
import { getApiErrorMessage } from '../../lib/apiError'
import type { UserProfile } from '../../types/user'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { Input } from '../ui/Input'

const AGE_RANGES = ['Under 18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']

interface FormValues {
  name: string
  age_range: string
  gender_preference: string
  country_region: string
  measurement_system: 'metric' | 'imperial'
}

export function BasicInfoForm() {
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)
  const { data, isLoading } = useQuery({ queryKey: ['profile'], queryFn: getProfile })

  const { register, handleSubmit, formState } = useForm<FormValues>({
    values: data
      ? {
          name: data.name ?? '',
          age_range: data.age_range ?? '',
          gender_preference: data.gender_preference ?? '',
          country_region: data.country_region ?? '',
          measurement_system: data.measurement_system,
        }
      : undefined,
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) => updateProfile(values),
    onSuccess: (updated: UserProfile) => {
      queryClient.setQueryData(['profile'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (isLoading) return <Card title="Basic info">Loading...</Card>

  return (
    <Card title="Basic info">
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-4"
      >
        <Input label="Name" {...register('name')} />

        <div className="flex flex-col gap-1">
          <label htmlFor="age_range" className="text-sm font-medium text-neutral-700">
            Age range
          </label>
          <select
            id="age_range"
            {...register('age_range')}
            className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
          >
            <option value="">Prefer not to say</option>
            {AGE_RANGES.map((range) => (
              <option key={range} value={range}>
                {range}
              </option>
            ))}
          </select>
        </div>

        <Input
          label="Clothing preference"
          placeholder="e.g. Men's, Women's, Unisex, no preference"
          {...register('gender_preference')}
        />
        <Input label="Country / region" {...register('country_region')} />

        <div>
          <p className="mb-1 text-sm font-medium text-neutral-700">Measurement system</p>
          <div className="flex gap-4 text-sm text-neutral-700">
            <label className="flex items-center gap-2">
              <input type="radio" value="metric" {...register('measurement_system')} />
              Metric (cm, kg)
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" value="imperial" {...register('measurement_system')} />
              Imperial (in, lb)
            </label>
          </div>
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
