import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getMeasurements, updateMeasurements } from '../../api/profile'
import { getApiErrorMessage } from '../../lib/apiError'
import { BODY_SHAPES, FIT_PREFERENCES } from '../../lib/profileOptions'
import type { BodyMeasurement } from '../../types/user'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { Input } from '../ui/Input'

// Every field in this form is a plain string in form state, even the
// numeric ones — converting "" to null explicitly at submit time is much
// easier to reason about than RHF's valueAsNumber (which turns "" into
// NaN). Saving always sends exactly what's on screen.
interface FormValues {
  height_cm: string
  weight_kg: string
  usual_shirt_size: string
  usual_pants_size: string
  usual_dress_size: string
  chest_cm: string
  waist_cm: string
  hip_cm: string
  shoulder_cm: string
  inseam_cm: string
  arm_length_cm: string
  leg_length_cm: string
  foot_size: string
  fit_preference: string
  body_shape: string
}

function toStringValue(n: number | null): string {
  return n === null ? '' : String(n)
}

function toNumberOrNull(s: string): number | null {
  const trimmed = s.trim()
  return trimmed === '' ? null : Number(trimmed)
}

function toStringOrNull(s: string): string | null {
  return s === '' ? null : s
}

export function MeasurementsForm() {
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)
  const [showAccurate, setShowAccurate] = useState(false)
  const { data, isLoading } = useQuery({
    queryKey: ['measurements'],
    queryFn: getMeasurements,
  })

  // If the user already saved any detailed measurement previously, open
  // the section by default instead of hiding their own saved data.
  useEffect(() => {
    if (!data) return
    const hasAccurateData =
      data.chest_cm !== null ||
      data.waist_cm !== null ||
      data.hip_cm !== null ||
      data.shoulder_cm !== null ||
      data.inseam_cm !== null ||
      data.arm_length_cm !== null ||
      data.leg_length_cm !== null ||
      data.foot_size !== null ||
      data.fit_preference !== null ||
      data.body_shape !== null
    if (hasAccurateData) setShowAccurate(true)
  }, [data])

  const { register, handleSubmit, formState } = useForm<FormValues>({
    values: data
      ? {
          height_cm: toStringValue(data.height_cm),
          weight_kg: toStringValue(data.weight_kg),
          usual_shirt_size: data.usual_shirt_size ?? '',
          usual_pants_size: data.usual_pants_size ?? '',
          usual_dress_size: data.usual_dress_size ?? '',
          chest_cm: toStringValue(data.chest_cm),
          waist_cm: toStringValue(data.waist_cm),
          hip_cm: toStringValue(data.hip_cm),
          shoulder_cm: toStringValue(data.shoulder_cm),
          inseam_cm: toStringValue(data.inseam_cm),
          arm_length_cm: toStringValue(data.arm_length_cm),
          leg_length_cm: toStringValue(data.leg_length_cm),
          foot_size: toStringValue(data.foot_size),
          fit_preference: data.fit_preference ?? '',
          body_shape: data.body_shape ?? '',
        }
      : undefined,
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      updateMeasurements({
        height_cm: toNumberOrNull(values.height_cm),
        weight_kg: toNumberOrNull(values.weight_kg),
        usual_shirt_size: toStringOrNull(values.usual_shirt_size),
        usual_pants_size: toStringOrNull(values.usual_pants_size),
        usual_dress_size: toStringOrNull(values.usual_dress_size),
        chest_cm: toNumberOrNull(values.chest_cm),
        waist_cm: toNumberOrNull(values.waist_cm),
        hip_cm: toNumberOrNull(values.hip_cm),
        shoulder_cm: toNumberOrNull(values.shoulder_cm),
        inseam_cm: toNumberOrNull(values.inseam_cm),
        arm_length_cm: toNumberOrNull(values.arm_length_cm),
        leg_length_cm: toNumberOrNull(values.leg_length_cm),
        foot_size: toNumberOrNull(values.foot_size),
        fit_preference:
          (toStringOrNull(values.fit_preference) as BodyMeasurement['fit_preference']) ??
          null,
        body_shape:
          (toStringOrNull(values.body_shape) as BodyMeasurement['body_shape']) ?? null,
      }),
    onSuccess: (updated: BodyMeasurement) => {
      queryClient.setQueryData(['measurements'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (isLoading) return <Card title="Body measurements">Loading...</Card>

  return (
    <Card title="Body measurements">
      <p className="mb-4 text-xs text-neutral-400">
        Everything here is optional. These help estimate your size — they
        never guarantee fit.
      </p>
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-4"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Height (cm)" inputMode="decimal" {...register('height_cm')} />
          <Input label="Weight (kg)" inputMode="decimal" {...register('weight_kg')} />
          <Input label="Usual shirt size" {...register('usual_shirt_size')} />
          <Input label="Usual pants size" {...register('usual_pants_size')} />
          <Input label="Usual dress size" {...register('usual_dress_size')} />
        </div>

        {!showAccurate && (
          <button
            type="button"
            onClick={() => setShowAccurate(true)}
            className="self-start text-sm font-medium text-neutral-900 underline"
          >
            Add detailed measurements (optional)
          </button>
        )}

        {showAccurate && (
          <div className="grid gap-4 border-t border-neutral-200 pt-4 sm:grid-cols-2">
            <Input label="Chest / bust (cm)" inputMode="decimal" {...register('chest_cm')} />
            <Input label="Waist (cm)" inputMode="decimal" {...register('waist_cm')} />
            <Input label="Hip (cm)" inputMode="decimal" {...register('hip_cm')} />
            <Input label="Shoulder (cm)" inputMode="decimal" {...register('shoulder_cm')} />
            <Input label="Inseam (cm)" inputMode="decimal" {...register('inseam_cm')} />
            <Input label="Arm length (cm)" inputMode="decimal" {...register('arm_length_cm')} />
            <Input label="Leg length (cm)" inputMode="decimal" {...register('leg_length_cm')} />
            <Input label="Foot size" inputMode="decimal" {...register('foot_size')} />

            <div className="flex flex-col gap-1">
              <label htmlFor="fit_preference" className="text-sm font-medium text-neutral-700">
                Fit preference
              </label>
              <select
                id="fit_preference"
                {...register('fit_preference')}
                className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
              >
                <option value="">Not set</option>
                {FIT_PREFERENCES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="body_shape" className="text-sm font-medium text-neutral-700">
                Body shape
              </label>
              <select
                id="body_shape"
                {...register('body_shape')}
                className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
              >
                <option value="">Prefer not to say</option>
                {BODY_SHAPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

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
