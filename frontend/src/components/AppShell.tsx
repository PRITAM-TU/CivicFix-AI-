import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Shield,
  LayoutDashboard,
  FilePlus2,
  Map,
  LogOut,
  Menu,
  X,
  Settings,
  Bell,
  ChevronRight,
  Activity,
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'

// ── Nav Item Definition ───────────────────────────────────────
interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  roles?: Array<'citizen' | 'officer' | 'admin'>
  badge?: string
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Citizen Portal', href: '/dashboard', icon: LayoutDashboard, roles: ['citizen', 'admin'] },
  { label: 'Report Issue',  href: '/report',    icon: FilePlus2,       roles: ['citizen'] },
  { label: 'Officer Queue', href: '/officer',   icon: Activity,        roles: ['officer'] },
  { label: 'Admin Panel',   href: '/admin',     icon: Settings,        roles: ['admin'] },
  { label: 'GIS Analytics', href: '/analytics', icon: Map,             roles: ['citizen', 'officer', 'admin'] },
]

type UserRole = 'citizen' | 'officer' | 'admin'

// ── Sidebar Component ─────────────────────────────────────────
interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const userRole = (user?.role || 'citizen') as UserRole

  const visibleItems = NAV_ITEMS.filter((item) =>
    !item.roles || item.roles.includes(userRole)
  )

  const handleLogout = () => {
    logout()
    navigate('/login')
    onClose()
  }

  // Close sidebar on route change on mobile
  useEffect(() => {
    onClose()
  }, [location.pathname]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar panel */}
      <nav
        className={`sidebar ${isOpen ? 'open' : ''}`}
        aria-label="Main navigation"
        role="navigation"
      >
        {/* Brand */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10">
          <div className="w-8 h-8 rounded-lg bg-white/15 flex items-center justify-center shrink-0" aria-hidden="true">
            <Shield size={18} className="text-white" />
          </div>
          <div>
            <div className="text-white font-bold text-[1.0625rem] leading-tight">CivicFix AI</div>
            <div className="text-white/50 text-[0.6875rem] font-mono uppercase tracking-wider mt-0.5">Autonomous Civic</div>
          </div>
          {/* Close on mobile */}
          <button
            onClick={onClose}
            aria-label="Close navigation"
            className="ml-auto icon-btn text-white/60 hover:text-white hover:bg-white/10 lg:hidden"
          >
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        {/* Nav Links */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <p className="section-label px-2 mb-3 text-white/30">Navigation</p>
          {visibleItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href ||
              (item.href !== '/' && location.pathname.startsWith(item.href))
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`nav-link ${isActive ? 'active' : ''}`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon size={18} aria-hidden="true" />
                <span className="flex-1">{item.label}</span>
                {item.badge && (
                  <span className="text-xs font-bold bg-red-500 text-white px-1.5 py-0.5 rounded-full font-mono">
                    {item.badge}
                  </span>
                )}
                {isActive && <ChevronRight size={14} className="opacity-60" aria-hidden="true" />}
              </Link>
            )
          })}
        </div>

        {/* User section */}
        {user && (
          <div className="p-3 border-t border-white/10 shrink-0">
            <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/10 mb-2">
              {/* Avatar */}
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white font-bold text-sm shrink-0" aria-hidden="true">
                {(user.full_name || user.email)[0].toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-white text-sm font-semibold truncate">{user.full_name}</div>
                <div className="text-white/50 text-xs font-mono capitalize">{user.role}</div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="nav-link w-full text-left"
              aria-label="Sign out of CivicFix AI"
            >
              <LogOut size={16} aria-hidden="true" />
              Sign Out
            </button>
          </div>
        )}
      </nav>
    </>
  )
}

// ── Top Bar (Mobile) ──────────────────────────────────────────
interface TopBarProps {
  onMenuOpen: () => void
  title?: string
}

const TopBar: React.FC<TopBarProps> = ({ onMenuOpen, title }) => {
  const { user } = useAuthStore()
  const location = useLocation()

  // Derive page title from route
  const pageTitle = title || NAV_ITEMS.find(
    (n) => location.pathname === n.href || (n.href !== '/' && location.pathname.startsWith(n.href))
  )?.label || 'CivicFix AI'

  return (
    <header className="topbar" role="banner">
      <button
        id="menu-open-btn"
        onClick={onMenuOpen}
        aria-label="Open navigation menu"
        aria-expanded={false}
        className="icon-btn shrink-0"
      >
        <Menu size={22} aria-hidden="true" />
      </button>

      <div className="flex items-center gap-2 min-w-0 flex-1">
        <Shield size={20} className="text-blue-700 shrink-0" aria-hidden="true" />
        <span className="font-bold text-gray-900 truncate">{pageTitle}</span>
      </div>

      {user && (
        <div className="flex items-center gap-1 shrink-0">
          <button
            aria-label="Notifications"
            className="icon-btn"
          >
            <Bell size={20} className="text-gray-500" aria-hidden="true" />
          </button>
          <div
            className="w-8 h-8 rounded-full bg-blue-900 flex items-center justify-center text-white text-sm font-bold shrink-0"
            aria-label={`Logged in as ${user.full_name}`}
          >
            {(user.full_name || user.email)[0].toUpperCase()}
          </div>
        </div>
      )}
    </header>
  )
}

// ── Bottom Navigation (Mobile) ────────────────────────────────
const BottomNav: React.FC = () => {
  const location = useLocation()
  const { user } = useAuthStore()
  const userRole = (user?.role || 'citizen') as UserRole

  const items = NAV_ITEMS.filter((item) =>
    !item.roles || item.roles.includes(userRole)
  )

  return (
    <nav className="bottom-nav" role="navigation" aria-label="Mobile navigation">
      {items.map((item) => {
        const Icon = item.icon
        const isActive = location.pathname === item.href ||
          (item.href !== '/' && location.pathname.startsWith(item.href))
        return (
          <Link
            key={item.href}
            to={item.href}
            className={`bottom-link ${isActive ? 'active' : ''}`}
            aria-current={isActive ? 'page' : undefined}
            aria-label={item.label}
          >
            <Icon size={22} aria-hidden="true" />
            <span>{item.label.split(' ')[0]}</span>
          </Link>
        )
      })}
    </nav>
  )
}

// ── AppShell ──────────────────────────────────────────────────
interface AppShellProps {
  children: React.ReactNode
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Trap focus when sidebar open on mobile
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [sidebarOpen])

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Mobile top bar */}
      <TopBar onMenuOpen={() => setSidebarOpen(true)} />

      {/* Main content */}
      <main className="app-main" id="main-content">
        <div className="app-content">
          {children}
        </div>
      </main>

      {/* Mobile bottom nav */}
      <BottomNav />
    </div>
  )
}

// ── Public Page Wrapper (landing, login, register) ─────────────
interface PublicShellProps {
  children: React.ReactNode
}

export const PublicShell: React.FC<PublicShellProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuthStore()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-dvh flex flex-col" style={{ background: 'var(--color-bg)' }}>
      {/* Public Navbar */}
      <header className="sticky top-0 z-40 bg-white border-b border-gray-200" role="banner">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-[60px] gap-4">
          {/* Brand */}
          <Link to="/" className="flex items-center gap-2.5 group" aria-label="CivicFix AI home">
            <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center shrink-0 group-hover:bg-blue-800 transition-colors" aria-hidden="true">
              <Shield size={17} className="text-white" />
            </div>
            <span className="font-bold text-gray-900 text-[1.0625rem] leading-tight">
              CivicFix <span className="text-blue-700">AI</span>
            </span>
          </Link>

          {/* Desktop links */}
          <nav className="hidden md:flex items-center gap-6" aria-label="Public navigation">
            {[
              { label: 'Home', href: '/' },
              { label: 'Dashboard', href: '/dashboard' },
              { label: 'Analytics', href: '/analytics' },
            ].map((l) => (
              <Link
                key={l.href}
                to={l.href}
                className={`text-sm font-medium transition-colors ${
                  location.pathname === l.href ? 'text-blue-700' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {l.label}
              </Link>
            ))}
          </nav>

          {/* Auth actions */}
          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <>
                <span className="hidden sm:block text-sm text-gray-600 font-medium">{user?.full_name?.split(' ')[0]}</span>
                <Link to="/dashboard" className="btn btn-primary btn-sm">Dashboard</Link>
              </>
            ) : (
              <>
                <Link to="/login" className="hidden sm:flex btn btn-secondary btn-sm">Sign In</Link>
                <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
              </>
            )}
            <button
              className="icon-btn md:hidden"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white px-4 py-3 space-y-1">
            {[
              { label: 'Home', href: '/' },
              { label: 'Dashboard', href: '/dashboard' },
              { label: 'Report Issue', href: '/report' },
              { label: 'Analytics', href: '/analytics' },
              { label: 'Sign In', href: '/login' },
            ].map((l) => (
              <Link
                key={l.href}
                to={l.href}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center px-3 h-12 rounded-xl text-sm font-medium text-gray-800 hover:bg-gray-50"
              >
                {l.label}
              </Link>
            ))}
          </div>
        )}
      </header>

      {/* Page content */}
      <div className="flex-1">
        {children}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-6" role="contentinfo">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-blue-900" aria-hidden="true" />
            <span className="text-sm font-semibold text-gray-700">CivicFix AI</span>
          </div>
          <p className="text-xs text-gray-400 font-mono text-center">
            LangGraph · FastAPI · PostGIS · Gemini Vision
          </p>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <Link to="/dashboard" className="text-xs text-gray-500 hover:text-gray-900">Dashboard</Link>
            ) : (
              <>
                <Link to="/login" className="text-xs text-gray-500 hover:text-gray-900">Sign In</Link>
                <Link to="/register" className="text-xs text-gray-500 hover:text-gray-900">Register</Link>
              </>
            )}
          </div>
        </div>
      </footer>
    </div>
  )
}

// ── Protected Route ───────────────────────────────────────────
import { Navigate } from 'react-router-dom'

interface ProtectedRouteProps {
  children: React.ReactNode
  roles?: Array<'citizen' | 'officer' | 'admin'>
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, roles }) => {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (roles && user && !roles.includes(user.role as UserRole)) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}
