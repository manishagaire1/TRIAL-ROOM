import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getClothes } from '../api/clothing'
import { deletePhoto, getPhotoStatus, uploadPhoto } from '../api/photo'
import { getSizeRecommendation } from '../api/sizeRecommendation'
import { getStyleRecommendation } from '../api/styleRecommendation'
import { createTryOnJob, getTryOnJob } from '../api/tryon'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { DisclaimerBanner } from '../components/ui/DisclaimerBanner'
import { useAuth } from '../hooks/useAuth'
import { useAuthedImageUrl } from '../hooks/useAuthedImageUrl'
import { getApiErrorMessage } from '../lib/apiError'
import { getColorHex } from '../lib/colorSwatches'
import type { ClothingListItem } from '../types/clothing'

export function TrialRoomPage() {
  const { user, ensureSession } = useAuth()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [selectedClothing, setSelectedClothing] = useState<ClothingListItem | null>(
    null,
  )
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  const [selectedColor, setSelectedColor] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobError, setJobError] = useState<string | null>(null)

  const catalogQuery = useQuery({ queryKey: ['clothes'], queryFn: getClothes })

  const photoStatusQuery = useQuery({
    queryKey: ['photo-status'],
    queryFn: getPhotoStatus,
    enabled: Boolean(user),
  })
  const hasPhoto = photoStatusQuery.data?.has_photo ?? false
  const { url: photoUrl } = useAuthedImageUrl(hasPhoto ? '/users/photo/file' : null)

  const jobQuery = useQuery({
    queryKey: ['tryon-job', jobId],
    queryFn: () => getTryOnJob(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'pending' || status === 'processing' ? 1500 : false
    },
  })
  const job = jobQuery.data
  const { url: resultUrl } = useAuthedImageUrl(
    job?.status === 'completed' && job.result ? job.result.image_url : null,
  )

  const uploadMutation = useMutation({
    mutationFn: uploadPhoto,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['photo-status'] }),
  })
  const deletePhotoMutation = useMutation({
    mutationFn: deletePhoto,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['photo-status'] }),
  })

  const handlePhotoChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await ensureSession()
    uploadMutation.mutate(file)
  }

  const handleRemovePhoto = () => {
    deletePhotoMutation.mutate()
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleSelectClothing = (item: ClothingListItem) => {
    setSelectedClothing(item)
    setSelectedSize(null)
    setSelectedColor(item.primary_color)
    setJobId(null)
    setJobError(null)
    // Fire-and-forget: a size recommendation is a helpful assist, not a
    // required step — if this fails, the user can still pick a size
    // manually, so we don't block selection on it.
    ensureSession().catch(() => {})
  }

  const sizeRecommendationQuery = useQuery({
    queryKey: ['size-recommendation', selectedClothing?.id],
    queryFn: () => getSizeRecommendation({ clothing_id: selectedClothing!.id }),
    enabled: Boolean(selectedClothing && user),
  })

  const styleRecommendationQuery = useQuery({
    queryKey: ['style-recommendation', selectedClothing?.id],
    queryFn: () => getStyleRecommendation({ clothing_id: selectedClothing!.id }),
    enabled: Boolean(selectedClothing && user),
  })

  const canGenerate = Boolean(hasPhoto && selectedClothing && selectedSize && selectedColor)
  const isGenerating = job?.status === 'pending' || job?.status === 'processing'

  const handleGenerate = async () => {
    if (!selectedClothing || !selectedSize || !selectedColor) return
    setJobError(null)
    try {
      await ensureSession()
      const newJob = await createTryOnJob({
        clothing_id: selectedClothing.id,
        selected_size: selectedSize,
        selected_color: selectedColor,
      })
      setJobId(newJob.id)
    } catch (err) {
      setJobError(getApiErrorMessage(err))
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Trial Room</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Your photo" className="flex flex-col gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handlePhotoChange}
          />

          {hasPhoto && photoUrl ? (
            <>
              <img
                src={photoUrl}
                alt="Your uploaded photo"
                className="aspect-3/4 w-full rounded-md object-cover"
              />
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadMutation.isPending}
                >
                  Replace
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleRemovePhoto}
                  disabled={deletePhotoMutation.isPending}
                >
                  Delete
                </Button>
              </div>
            </>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadMutation.isPending}
              className="flex aspect-3/4 w-full flex-col items-center justify-center gap-2 rounded-md border-2 border-dashed border-neutral-300 text-center text-sm text-neutral-500 hover:border-neutral-400"
            >
              <span>{uploadMutation.isPending ? 'Uploading...' : 'Upload a full-body photo'}</span>
              <span className="text-xs text-neutral-400">
                Good lighting, clear background, no group photos
              </span>
            </button>
          )}
          {uploadMutation.isError && (
            <p className="text-sm text-red-600">{getApiErrorMessage(uploadMutation.error)}</p>
          )}
        </Card>

        <Card title="Try-on result" className="flex flex-col gap-3">
          <DisclaimerBanner message="AI visualization is an approximation, not a guarantee of fit." />
          <div className="flex aspect-3/4 w-full items-center justify-center rounded-md bg-neutral-100 text-center text-sm text-neutral-500">
            {job?.status === 'completed' && resultUrl ? (
              <img
                src={resultUrl}
                alt={`Try-on result: ${job.clothing_name}`}
                className="h-full w-full rounded-md object-cover"
              />
            ) : isGenerating ? (
              <p className="px-6">Preparing your virtual try-on...</p>
            ) : job?.status === 'failed' ? (
              <p className="px-6 text-red-600">
                {job.failure_reason ?? 'The try-on could not be generated.'}
              </p>
            ) : (
              <p className="px-6">
                Upload a photo, pick clothing, a color, and a size, then generate a
                try-on.
              </p>
            )}
          </div>
          {jobError && <p className="text-sm text-red-600">{jobError}</p>}
          <Button disabled={!canGenerate || isGenerating} onClick={handleGenerate}>
            {isGenerating ? 'Generating...' : 'Generate try-on'}
          </Button>
        </Card>

        <Card title="Select clothing" className="flex flex-col gap-3">
          {catalogQuery.isLoading && (
            <p className="text-sm text-neutral-500">Loading catalog...</p>
          )}
          {catalogQuery.isError && (
            <p className="text-sm text-red-600">
              Couldn't load the catalog. Is the backend running?
            </p>
          )}

          <div className="flex flex-col gap-2">
            {catalogQuery.data?.items.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSelectClothing(item)}
                className={`flex items-center gap-3 rounded-md border p-2 text-left transition-colors ${
                  selectedClothing?.id === item.id
                    ? 'border-neutral-900 bg-neutral-50'
                    : 'border-neutral-200 hover:border-neutral-400'
                }`}
              >
                <span
                  className="h-10 w-10 shrink-0 rounded-md"
                  style={{ backgroundColor: getColorHex(item.primary_color) }}
                  aria-hidden
                />
                <span className="flex-1">
                  <span className="block text-sm font-medium text-neutral-900">
                    {item.name}
                  </span>
                  <span className="block text-xs text-neutral-500">
                    {item.primary_color} · ${item.price}
                  </span>
                </span>
              </button>
            ))}
          </div>

          {selectedClothing && (
            <>
              <div>
                <p className="mb-2 text-sm font-medium text-neutral-700">Color</p>
                <div className="flex flex-wrap gap-2">
                  {selectedClothing.available_colors.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setSelectedColor(color)}
                      aria-pressed={selectedColor === color}
                      title={color}
                      className={`h-8 w-8 rounded-full border-2 ${
                        selectedColor === color ? 'border-neutral-900' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: getColorHex(color) }}
                    />
                  ))}
                </div>
              </div>

              {sizeRecommendationQuery.data?.recommended_size && (
                <div className="rounded-md border border-neutral-200 bg-neutral-50 p-3 text-sm">
                  <p className="font-medium text-neutral-900">
                    Suggested size: {sizeRecommendationQuery.data.recommended_size}
                    {sizeRecommendationQuery.data.estimated_fit &&
                      ` (${sizeRecommendationQuery.data.estimated_fit} fit)`}
                  </p>
                  <p className="mt-1 text-neutral-600">
                    {sizeRecommendationQuery.data.explanation}
                  </p>
                  <p className="mt-1 text-xs text-neutral-400">
                    This is an estimate based on the information provided and the
                    product's size chart. Actual fit may vary.
                  </p>
                  <button
                    type="button"
                    onClick={() =>
                      setSelectedSize(sizeRecommendationQuery.data!.recommended_size)
                    }
                    className="mt-2 text-sm font-medium text-neutral-900 underline"
                  >
                    Use this size
                  </button>
                </div>
              )}
              {sizeRecommendationQuery.data && !sizeRecommendationQuery.data.recommended_size && (
                <p className="text-sm text-neutral-500">
                  {sizeRecommendationQuery.data.explanation}
                </p>
              )}

              <div>
                <p className="mb-2 text-sm font-medium text-neutral-700">Size</p>
                <div className="flex flex-wrap gap-2">
                  {selectedClothing.available_sizes.map((size) => (
                    <button
                      key={size}
                      type="button"
                      onClick={() => setSelectedSize(size)}
                      className={`rounded-md border px-3 py-1 text-sm transition-colors ${
                        selectedSize === size
                          ? 'border-neutral-900 bg-neutral-900 text-white'
                          : 'border-neutral-300 text-neutral-700 hover:border-neutral-400'
                      }`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </Card>
      </div>

      {selectedClothing && styleRecommendationQuery.data && (
        <Card title="Complete the outfit">
          {styleRecommendationQuery.data.suggestions.length === 0 ? (
            <p className="text-sm text-neutral-500">
              No strongly matching items were found in the catalog yet.
            </p>
          ) : (
            <>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {styleRecommendationQuery.data.suggestions.map((suggestion) => (
                  <button
                    key={suggestion.clothing_id}
                    type="button"
                    onClick={() => {
                      const fullItem = catalogQuery.data?.items.find(
                        (item) => item.id === suggestion.clothing_id,
                      )
                      if (fullItem) handleSelectClothing(fullItem)
                    }}
                    className="flex items-start gap-3 rounded-md border border-neutral-200 p-3 text-left hover:border-neutral-400"
                  >
                    <span
                      className="h-10 w-10 shrink-0 rounded-md"
                      style={{ backgroundColor: getColorHex(suggestion.primary_color) }}
                      aria-hidden
                    />
                    <span>
                      <span className="block text-sm font-medium text-neutral-900">
                        {suggestion.name}
                      </span>
                      <span className="block text-xs uppercase tracking-wide text-neutral-400">
                        {suggestion.slot}
                      </span>
                      <span className="mt-1 block text-xs text-neutral-500">
                        {suggestion.reason}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
              <p className="mt-3 text-xs text-neutral-400">{styleRecommendationQuery.data.note}</p>
            </>
          )}
        </Card>
      )}
    </div>
  )
}
