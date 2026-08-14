import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { compareOutfits, deleteOutfit, getOutfits, updateOutfit } from '../api/outfits'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { getApiErrorMessage } from '../lib/apiError'
import { getColorHex } from '../lib/colorSwatches'
import { OCCASIONS } from '../lib/profileOptions'
import type { CompareResponse, SavedOutfit } from '../types/outfit'

const MAX_COMPARE = 3

export function SavedOutfitsPage() {
  const queryClient = useQueryClient()
  const outfitsQuery = useQuery({ queryKey: ['outfits'], queryFn: getOutfits })

  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [occasion, setOccasion] = useState('')
  const [comparison, setComparison] = useState<CompareResponse | null>(null)

  const likeMutation = useMutation({
    mutationFn: ({ id, liked }: { id: string; liked: boolean }) => updateOutfit(id, { liked }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['outfits'] }),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteOutfit(id),
    onSuccess: (_data, id) => {
      setSelectedIds((prev) => prev.filter((x) => x !== id))
      queryClient.invalidateQueries({ queryKey: ['outfits'] })
    },
  })
  const compareMutation = useMutation({
    mutationFn: () => compareOutfits(selectedIds, occasion || undefined),
    onSuccess: setComparison,
  })

  const toggleSelected = (id: string) => {
    setComparison(null)
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id)
      if (prev.length >= MAX_COMPARE) return prev
      return [...prev, id]
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Saved Outfits</h1>

      {outfitsQuery.data?.items.length === 0 && (
        <p className="text-sm text-neutral-500">
          No saved outfits yet — save one from your Trial History.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {outfitsQuery.data?.items.map((outfit) => (
          <OutfitCard
            key={outfit.id}
            outfit={outfit}
            selected={selectedIds.includes(outfit.id)}
            onToggleSelect={() => toggleSelected(outfit.id)}
            onToggleLike={() =>
              likeMutation.mutate({ id: outfit.id, liked: !outfit.liked })
            }
            onDelete={() => deleteMutation.mutate(outfit.id)}
          />
        ))}
      </div>

      {selectedIds.length >= 2 && (
        <Card title={`Compare ${selectedIds.length} outfits`}>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <label htmlFor="compare-occasion" className="text-sm font-medium text-neutral-700">
                Occasion (optional)
              </label>
              <select
                id="compare-occasion"
                value={occasion}
                onChange={(e) => setOccasion(e.target.value)}
                className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
              >
                <option value="">None</option>
                {OCCASIONS.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </div>
            <Button onClick={() => compareMutation.mutate()} disabled={compareMutation.isPending}>
              {compareMutation.isPending ? 'Comparing...' : 'Compare selected'}
            </Button>
          </div>
          {compareMutation.isError && (
            <p className="mt-2 text-sm text-red-600">{getApiErrorMessage(compareMutation.error)}</p>
          )}

          {comparison && (
            <div className="mt-4 flex flex-col gap-3">
              <div className="grid gap-3 sm:grid-cols-3">
                {comparison.entries.map((entry) => (
                  <div
                    key={entry.outfit.id}
                    className={`rounded-md border p-3 text-sm ${
                      entry.is_strongest_match
                        ? 'border-neutral-900 bg-neutral-50'
                        : 'border-neutral-200'
                    }`}
                  >
                    <p className="font-medium text-neutral-900">
                      {entry.outfit.name}
                      {entry.is_strongest_match && ' ★'}
                    </p>
                    <p className="mt-1 text-neutral-600">{entry.explanation}</p>
                  </div>
                ))}
              </div>
              <p className="text-sm text-neutral-700">{comparison.summary}</p>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}

function OutfitCard({
  outfit,
  selected,
  onToggleSelect,
  onToggleLike,
  onDelete,
}: {
  outfit: SavedOutfit
  selected: boolean
  onToggleSelect: () => void
  onToggleLike: () => void
  onDelete: () => void
}) {
  return (
    <Card className={selected ? 'ring-2 ring-neutral-900' : ''}>
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-neutral-900">{outfit.name}</p>
        <button
          type="button"
          onClick={onToggleLike}
          aria-pressed={outfit.liked}
          className="text-lg"
          title={outfit.liked ? 'Unlike' : 'Like'}
        >
          {outfit.liked ? '♥' : '♡'}
        </button>
      </div>
      {outfit.occasion && (
        <p className="text-xs uppercase tracking-wide text-neutral-400">{outfit.occasion}</p>
      )}
      <div className="mt-2 flex flex-col gap-1">
        {outfit.items.map((item) => (
          <div key={item.clothing_id} className="flex items-center gap-2 text-sm">
            <span
              className="h-4 w-4 shrink-0 rounded-full"
              style={{ backgroundColor: getColorHex(item.primary_color) }}
              aria-hidden
            />
            <span className="text-neutral-700">{item.name}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <label className="flex flex-1 items-center gap-2 text-sm text-neutral-600">
          <input type="checkbox" checked={selected} onChange={onToggleSelect} />
          Compare
        </label>
        <button type="button" onClick={onDelete} className="text-sm text-red-600 underline">
          Delete
        </button>
      </div>
    </Card>
  )
}
