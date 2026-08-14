import { useEffect, useRef, useState } from 'react'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { DisclaimerBanner } from '../components/ui/DisclaimerBanner'
import { sampleClothing } from '../lib/sampleData'
import type { ClothingItem } from '../types/clothing'

type GenerateState = 'idle' | 'not-connected'

export function TrialRoomPage() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [photoUrl, setPhotoUrl] = useState<string | null>(null)
  const [selectedClothing, setSelectedClothing] = useState<ClothingItem | null>(null)
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  const [generateState, setGenerateState] = useState<GenerateState>('idle')

  // Photo preview happens entirely in the browser (no upload yet — that
  // needs the backend from Phase 4). Object URLs must be revoked when
  // replaced or when the page unmounts, or the browser leaks memory.
  useEffect(() => {
    return () => {
      if (photoUrl) URL.revokeObjectURL(photoUrl)
    }
  }, [photoUrl])

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (photoUrl) URL.revokeObjectURL(photoUrl)
    setPhotoUrl(URL.createObjectURL(file))
    setGenerateState('idle')
  }

  const handleRemovePhoto = () => {
    if (photoUrl) URL.revokeObjectURL(photoUrl)
    setPhotoUrl(null)
    setGenerateState('idle')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleSelectClothing = (item: ClothingItem) => {
    setSelectedClothing(item)
    setSelectedSize(null)
    setGenerateState('idle')
  }

  const canGenerate = Boolean(photoUrl && selectedClothing && selectedSize)

  const handleGenerate = () => {
    // There is no AI provider wired up yet (that's Phase 7). We show an
    // honest "not connected" state instead of a fake generated image —
    // faking an AI result here would violate the project's core promise.
    setGenerateState('not-connected')
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

          {photoUrl ? (
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
                >
                  Replace
                </Button>
                <Button variant="secondary" onClick={handleRemovePhoto}>
                  Delete
                </Button>
              </div>
            </>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex aspect-3/4 w-full flex-col items-center justify-center gap-2 rounded-md border-2 border-dashed border-neutral-300 text-center text-sm text-neutral-500 hover:border-neutral-400"
            >
              <span>Upload a full-body photo</span>
              <span className="text-xs text-neutral-400">
                Good lighting, clear background, no group photos
              </span>
            </button>
          )}
        </Card>

        <Card title="Try-on result" className="flex flex-col gap-3">
          <DisclaimerBanner message="AI visualization is an approximation, not a guarantee of fit." />
          <div className="flex aspect-3/4 w-full items-center justify-center rounded-md bg-neutral-100 text-center text-sm text-neutral-500">
            {generateState === 'not-connected' ? (
              <p className="px-6">
                The AI try-on provider isn't connected yet — this gets built
                in Phase 7. This screen will show your generated result here.
              </p>
            ) : (
              <p className="px-6">
                Upload a photo, pick clothing and a size, then generate a
                try-on.
              </p>
            )}
          </div>
          <Button disabled={!canGenerate} onClick={handleGenerate}>
            Generate try-on
          </Button>
        </Card>

        <Card title="Select clothing" className="flex flex-col gap-3">
          <div className="flex flex-col gap-2">
            {sampleClothing.map((item) => (
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
                  style={{ backgroundColor: item.swatch }}
                  aria-hidden
                />
                <span className="flex-1">
                  <span className="block text-sm font-medium text-neutral-900">
                    {item.name}
                  </span>
                  <span className="block text-xs text-neutral-500">
                    {item.color} · ${item.price}
                  </span>
                </span>
              </button>
            ))}
          </div>

          {selectedClothing && (
            <div>
              <p className="mb-2 text-sm font-medium text-neutral-700">Size</p>
              <div className="flex flex-wrap gap-2">
                {selectedClothing.sizes.map((size) => (
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
          )}

          <p className="text-xs text-neutral-400">
            Sample catalog shown — real products connect in Phase 6.
          </p>
        </Card>
      </div>
    </div>
  )
}
