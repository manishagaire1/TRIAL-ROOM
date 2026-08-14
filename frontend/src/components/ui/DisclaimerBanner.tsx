interface DisclaimerBannerProps {
  message: string
}

/**
 * Renders the product-honesty disclaimers required throughout the app
 * (docs/01-product-requirements.md, Section 5). Used wherever AI try-on,
 * size, or style output is shown, so the wording can't drift page to page.
 */
export function DisclaimerBanner({ message }: DisclaimerBannerProps) {
  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      {message}
    </div>
  )
}
