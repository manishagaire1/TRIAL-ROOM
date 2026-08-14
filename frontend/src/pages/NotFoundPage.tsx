import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-10 text-center">
      <h1 className="text-2xl font-semibold text-neutral-900">Page not found</h1>
      <p className="mt-2 text-neutral-500">
        The page you're looking for doesn't exist.
      </p>
      <Link
        to="/"
        className="mt-4 inline-block text-sm font-medium text-neutral-900 underline"
      >
        Back to home
      </Link>
    </div>
  )
}
