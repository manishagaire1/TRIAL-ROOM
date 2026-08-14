import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getTryOnHistory } from '../api/tryon'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { sampleDashboardStats } from '../lib/sampleData'

export function DashboardPage() {
  const stats = sampleDashboardStats
  const historyQuery = useQuery({ queryKey: ['tryon-history'], queryFn: getTryOnHistory })
  const recentTryOnsCount = historyQuery.data?.total ?? 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-neutral-900">Dashboard</h1>
        <Link to="/trial-room">
          <Button>Start a try-on</Button>
        </Link>
      </div>

      <Card title="Profile completion">
        <div className="h-2 w-full overflow-hidden rounded-full bg-neutral-100">
          <div
            className="h-full rounded-full bg-neutral-900"
            style={{ width: `${stats.profileCompletionPercent}%` }}
          />
        </div>
        <p className="mt-2 text-sm text-neutral-500">
          {stats.profileCompletionPercent}% complete — add body measurements
          and style preferences to get better recommendations.
        </p>
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card title="Recent try-ons">
          <EmptyState
            text={
              recentTryOnsCount === 0
                ? "You haven't tried anything on yet."
                : `${recentTryOnsCount} recent try-ons`
            }
          />
        </Card>
        <Card title="Saved outfits">
          <EmptyState
            text={
              stats.savedOutfitsCount === 0
                ? 'No saved outfits yet.'
                : `${stats.savedOutfitsCount} saved outfits`
            }
          />
        </Card>
        <Card title="Shopping list">
          <EmptyState
            text={
              stats.shoppingListCount === 0
                ? 'Your shopping list is empty.'
                : `${stats.shoppingListCount} items`
            }
          />
        </Card>
      </div>

      <p className="text-xs text-neutral-400">
        Recent try-ons reflect your real trial history. Saved outfits and
        shopping list are still placeholder data — those connect in a
        later phase.
      </p>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return <p className="text-sm text-neutral-500">{text}</p>
}
