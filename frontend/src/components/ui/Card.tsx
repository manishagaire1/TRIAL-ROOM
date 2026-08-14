import type { ReactNode } from 'react'

interface CardProps {
  title?: string
  children: ReactNode
  className?: string
}

export function Card({ title, children, className = '' }: CardProps) {
  return (
    <div
      className={`rounded-lg border border-neutral-200 bg-white p-5 ${className}`}
    >
      {title && (
        <h2 className="mb-3 text-sm font-semibold text-neutral-900">{title}</h2>
      )}
      {children}
    </div>
  )
}
