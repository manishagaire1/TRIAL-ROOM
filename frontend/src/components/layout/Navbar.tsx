import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Button } from '../ui/Button'

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `text-sm font-medium transition-colors hover:text-neutral-900 ${
    isActive ? 'text-neutral-900' : 'text-neutral-500'
  }`

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isRealAccount = Boolean(user && !user.is_guest)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <NavLink to="/" className="text-lg font-semibold text-neutral-900">
          VirtualFit AI
        </NavLink>

        <nav className="flex items-center gap-6">
          <NavLink to="/trial-room" className={navLinkClasses}>
            Trial Room
          </NavLink>
          {isRealAccount && (
            <>
              <NavLink to="/dashboard" className={navLinkClasses}>
                Dashboard
              </NavLink>
              <NavLink to="/history" className={navLinkClasses}>
                History
              </NavLink>
              <NavLink to="/outfits" className={navLinkClasses}>
                Outfits
              </NavLink>
              <NavLink to="/wardrobe" className={navLinkClasses}>
                Wardrobe
              </NavLink>
              <NavLink to="/profile" className={navLinkClasses}>
                Profile
              </NavLink>
            </>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {isRealAccount ? (
            <>
              <span className="text-sm text-neutral-500">{user!.email}</span>
              <Button variant="secondary" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : user?.is_guest ? (
            <>
              <span className="text-sm text-neutral-500">Browsing as guest</span>
              <NavLink
                to="/register"
                className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700"
              >
                Sign up to save
              </NavLink>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className="text-sm font-medium text-neutral-600 hover:text-neutral-900"
              >
                Log in
              </NavLink>
              <NavLink
                to="/register"
                className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700"
              >
                Sign up
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
