import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createOutfit, getOutfits } from '../api/outfits'
import { getTryOnHistory } from '../api/tryon'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAuthedImageUrl } from '../hooks/useAuthedImageUrl'
import { getApiErrorMessage } from '../lib/apiError'
import type { TryOnJob } from '../types/tryon'

export function TrialHistoryPage() {
  const queryClient = useQueryClient()
  const historyQuery = useQuery({ queryKey: ['tryon-history'], queryFn: getTryOnHistory })
  const outfitsQuery = useQuery({ queryKey: ['outfits'], queryFn: getOutfits })

  const savedClothingIds = new Set(
    outfitsQuery.data?.items.flatMap((outfit) => outfit.items.map((i) => i.clothing_id)) ?? [],
  )

  const saveMutation = useMutation({
    mutationFn: (clothingId: string) => createOutfit({ clothing_id: clothingId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['outfits'] }),
  })

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Trial History</h1>

      {historyQuery.isLoading && <p className="text-sm text-neutral-500">Loading...</p>}
      {historyQuery.data?.items.length === 0 && (
        <p className="text-sm text-neutral-500">
          You haven't tried anything on yet — head to the Trial Room to get started.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {historyQuery.data?.items.map((job) => (
          <HistoryCard
            key={job.id}
            job={job}
            alreadySaved={savedClothingIds.has(job.clothing_id)}
            onSave={() => saveMutation.mutate(job.clothing_id)}
            isSaving={saveMutation.isPending}
          />
        ))}
      </div>
      {saveMutation.isError && (
        <p className="text-sm text-red-600">{getApiErrorMessage(saveMutation.error)}</p>
      )}
    </div>
  )
}

function HistoryCard({
  job,
  alreadySaved,
  onSave,
  isSaving,
}: {
  job: TryOnJob
  alreadySaved: boolean
  onSave: () => void
  isSaving: boolean
}) {
  const { url } = useAuthedImageUrl(
    job.status === 'completed' && job.result ? job.result.image_url : null,
  )

  return (
    <Card>
      <div className="flex aspect-3/4 w-full items-center justify-center overflow-hidden rounded-md bg-neutral-100">
        {url ? (
          <img
            src={url}
            alt={`Try-on result: ${job.clothing_name}`}
            className="h-full w-full object-cover"
          />
        ) : (
          <span className="text-xs text-neutral-400">
            {job.status === 'failed' ? 'Failed' : job.status}
          </span>
        )}
      </div>
      <p className="mt-2 text-sm font-medium text-neutral-900">{job.clothing_name}</p>
      <p className="text-xs text-neutral-500">
        {job.selected_color} · {job.selected_size} ·{' '}
        {new Date(job.created_at).toLocaleDateString()}
      </p>
      {job.status === 'completed' && (
        <Button
          variant="secondary"
          className="mt-2 w-full"
          disabled={alreadySaved || isSaving}
          onClick={onSave}
        >
          {alreadySaved ? 'Saved as outfit' : 'Save as outfit'}
        </Button>
      )}
    </Card>
  )
}
