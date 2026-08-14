import { Link } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'

const pillars = [
  {
    title: 'Visual try-on',
    description:
      'See an AI-generated approximation of how a garment may look on you. A visualization, not a guarantee.',
  },
  {
    title: 'Size recommendation',
    description:
      'Get an estimated size based on your measurements and the product’s own size chart, with a confidence level.',
  },
  {
    title: 'Style recommendation',
    description:
      'Get outfit and color suggestions based on preferences you choose — never assumptions about you.',
  },
]

export function LandingPage() {
  return (
    <div className="flex flex-col gap-16">
      <section className="flex flex-col items-center gap-6 py-12 text-center">
        <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl">
          See it on you before you buy it
        </h1>
        <p className="max-w-xl text-lg text-neutral-500">
          Upload a photo, pick clothing, and get an AI visualization plus an
          honest size estimate — no guesswork, no false promises.
        </p>
        <div className="flex gap-3">
          <Link to="/trial-room">
            <Button>Try it now</Button>
          </Link>
          <Link to="/register">
            <Button variant="secondary">Create account</Button>
          </Link>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {pillars.map((pillar) => (
          <Card key={pillar.title} title={pillar.title}>
            <p className="text-sm text-neutral-600">{pillar.description}</p>
          </Card>
        ))}
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-neutral-900">
          Good to know before you start
        </h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-neutral-600">
          <li>AI try-on is a visualization, not a guarantee of fit.</li>
          <li>
            Size recommendations are estimates based on the information you
            provide and the product's size chart; actual fit varies by
            fabric, construction, and brand.
          </li>
          <li>AI-generated images may contain visual errors.</li>
        </ul>
      </section>
    </div>
  )
}
