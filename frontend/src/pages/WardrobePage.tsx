import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getClothes } from '../api/clothing'
import { createOutfit } from '../api/outfits'
import { deleteWardrobeItem, getWardrobe, uploadWardrobeItem } from '../api/wardrobe'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { useAuthedImageUrl } from '../hooks/useAuthedImageUrl'
import { getApiErrorMessage } from '../lib/apiError'
import { CATEGORIES, slotForCategory } from '../lib/categories'
import { OCCASIONS } from '../lib/profileOptions'
import type { OutfitItemInput } from '../types/outfit'
import type { WardrobeItem } from '../types/wardrobe'

const BUILDER_SLOTS: { key: string; label: string }[] = [
  { key: 'top', label: 'Top' },
  { key: 'bottom', label: 'Bottom' },
  { key: 'shoes', label: 'Shoes' },
  { key: 'accessory', label: 'Accessories' },
]

interface SlotOption {
  value: string // "catalog:<id>" or "wardrobe:<id>"
  label: string
}

export function WardrobePage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Wardrobe</h1>
      <UploadForm />
      <WardrobeGrid />
      <OutfitBuilder />
    </div>
  )
}

function UploadForm() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [category, setCategory] = useState(CATEGORIES[0])
  const [color, setColor] = useState('')
  const [label, setLabel] = useState('')

  const uploadMutation = useMutation({
    mutationFn: uploadWardrobeItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wardrobe'] })
      setColor('')
      setLabel('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const file = fileInputRef.current?.files?.[0]
    if (!file || !color) return
    uploadMutation.mutate({ file, category, color, label: label || undefined })
  }

  return (
    <Card title="Add to your wardrobe">
      <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          required
          className="text-sm"
        />
        <div className="flex flex-col gap-1">
          <label htmlFor="wardrobe-category" className="text-sm font-medium text-neutral-700">
            Category
          </label>
          <select
            id="wardrobe-category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <Input
          label="Color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
          placeholder="e.g. Black"
          required
        />
        <Input
          label="Label (optional)"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="e.g. Favorite hoodie"
        />
        <Button type="submit" disabled={uploadMutation.isPending}>
          {uploadMutation.isPending ? 'Uploading...' : 'Add item'}
        </Button>
      </form>
      {uploadMutation.isError && (
        <p className="mt-2 text-sm text-red-600">{getApiErrorMessage(uploadMutation.error)}</p>
      )}
    </Card>
  )
}

function WardrobeGrid() {
  const queryClient = useQueryClient()
  const wardrobeQuery = useQuery({ queryKey: ['wardrobe'], queryFn: getWardrobe })
  const deleteMutation = useMutation({
    mutationFn: deleteWardrobeItem,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['wardrobe'] }),
  })

  if (wardrobeQuery.data?.items.length === 0) {
    return (
      <p className="text-sm text-neutral-500">
        Your wardrobe is empty — add a photo of something you own above.
      </p>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {wardrobeQuery.data?.items.map((item) => (
        <WardrobeCard
          key={item.id}
          item={item}
          onDelete={() => deleteMutation.mutate(item.id)}
        />
      ))}
    </div>
  )
}

function WardrobeCard({ item, onDelete }: { item: WardrobeItem; onDelete: () => void }) {
  const { url } = useAuthedImageUrl(item.image_url)
  return (
    <Card>
      <div className="flex aspect-3/4 w-full items-center justify-center overflow-hidden rounded-md bg-neutral-100">
        {url && <img src={url} alt={item.label ?? item.category} className="h-full w-full object-cover" />}
      </div>
      <p className="mt-2 text-sm font-medium text-neutral-900">{item.label || item.category}</p>
      <p className="text-xs text-neutral-500">
        {item.category} · {item.color}
      </p>
      <button type="button" onClick={onDelete} className="mt-2 text-sm text-red-600 underline">
        Delete
      </button>
    </Card>
  )
}

function OutfitBuilder() {
  const catalogQuery = useQuery({ queryKey: ['clothes'], queryFn: getClothes })
  const wardrobeQuery = useQuery({ queryKey: ['wardrobe'], queryFn: getWardrobe })

  const [selection, setSelection] = useState<Record<string, string>>({})
  const [occasion, setOccasion] = useState('')
  const [name, setName] = useState('')
  const [savedMessage, setSavedMessage] = useState<string | null>(null)

  const buildMutation = useMutation({
    mutationFn: () => {
      const items: OutfitItemInput[] = Object.entries(selection)
        .filter(([, value]) => value)
        .map(([slot, value]) => {
          const [source, id] = value.split(':')
          return source === 'catalog'
            ? { clothing_id: id, slot }
            : { wardrobe_item_id: id, slot }
        })
      return createOutfit({ name: name || undefined, occasion: occasion || undefined, items })
    },
    onSuccess: (outfit) => {
      setSavedMessage(outfit.name)
      setSelection({})
      setName('')
    },
  })

  const optionsForSlot = (slotKey: string): SlotOption[] => {
    const catalogOptions = (catalogQuery.data?.items ?? [])
      .filter((item) => slotForCategory(item.category) === slotKey)
      .map((item) => ({ value: `catalog:${item.id}`, label: `${item.name} (catalog)` }))
    const wardrobeOptions = (wardrobeQuery.data?.items ?? [])
      .filter((item) => slotForCategory(item.category) === slotKey)
      .map((item) => ({
        value: `wardrobe:${item.id}`,
        label: `${item.label || item.category} (wardrobe)`,
      }))
    return [...catalogOptions, ...wardrobeOptions]
  }

  const hasAnySelection = Object.values(selection).some(Boolean)

  return (
    <Card title="Build an outfit">
      <p className="mb-3 text-xs text-neutral-400">
        Mix catalog products and your own wardrobe. An AI-generated visual for full
        combined outfits isn't available yet — this saves the outfit for
        comparison and reference.
      </p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {BUILDER_SLOTS.map(({ key, label: slotLabel }) => (
          <div key={key} className="flex flex-col gap-1">
            <label htmlFor={`slot-${key}`} className="text-sm font-medium text-neutral-700">
              {slotLabel}
            </label>
            <select
              id={`slot-${key}`}
              value={selection[key] ?? ''}
              onChange={(e) => setSelection((prev) => ({ ...prev, [key]: e.target.value }))}
              className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {optionsForSlot(key).map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <Input
          label="Outfit name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <div className="flex flex-col gap-1">
          <label htmlFor="builder-occasion" className="text-sm font-medium text-neutral-700">
            Occasion (optional)
          </label>
          <select
            id="builder-occasion"
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
        <Button
          onClick={() => buildMutation.mutate()}
          disabled={!hasAnySelection || buildMutation.isPending}
        >
          {buildMutation.isPending ? 'Saving...' : 'Generate outfit'}
        </Button>
      </div>

      {buildMutation.isError && (
        <p className="mt-2 text-sm text-red-600">{getApiErrorMessage(buildMutation.error)}</p>
      )}
      {savedMessage && (
        <p className="mt-2 text-sm text-green-600">
          Saved "{savedMessage}". View it on{' '}
          <Link to="/outfits" className="underline">
            Saved Outfits
          </Link>
          .
        </p>
      )}
    </Card>
  )
}
