import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { PublicShell } from '../components/AppShell'
import {
  ArrowRight,
  Shield,
  Eye,
  MapPin,
  GitMerge,
  TrendingUp,
  Mic,
  Bot,
  CheckCircle2,
  AlertTriangle,
  Zap,
  FileText,
  BarChart3,
  ChevronRight,
} from 'lucide-react'

const FEATURES = [
  {
    icon: Eye,
    title: 'Gemini Vision AI',
    desc: 'Automatically classifies and analyzes uploaded photos to detect issue type and severity.',
    badge: 'LIVE',
  },
  {
    icon: MapPin,
    title: 'PostGIS Spatial Intel',
    desc: 'GPS geocoding + ward-boundary lookup + 50m radius duplicate detection.',
  },
  {
    icon: GitMerge,
    title: '10-Agent LangGraph',
    desc: 'Supervisor-orchestrated DAG of Vision, Location, Validator, Dedup, Priority, Router, Verify agents.',
    badge: '10 Agents',
  },
  {
    icon: TrendingUp,
    title: 'SLA Enforcement',
    desc: 'Every complaint has a live SLA countdown. Auto-escalation when deadlines breach.',
  },
  {
    icon: Mic,
    title: 'Voice Intake',
    desc: 'Citizens speak their complaint. Whisper transcription feeds the same AI pipeline.',
  },
  {
    icon: Bot,
    title: 'Human-in-the-Loop',
    desc: 'Officers intercept AI decisions at any checkpoint — full control preserved.',
  },
]

const STATS = [
  { value: '10', label: 'AI Agents', sub: 'LangGraph Supervisor' },
  { value: '99.2%', label: 'SLA Compliance', sub: '30-day average' },
  { value: '<2s', label: 'Triage Speed', sub: 'Intake → Routing' },
  { value: '8', label: 'Pipeline Stages', sub: 'Vision → Verify' },
]

const PIPELINE = [
  { n: '01', label: 'Intake',     icon: FileText  },
  { n: '02', label: 'Vision AI',  icon: Eye       },
  { n: '03', label: 'GIS Map',    icon: MapPin    },
  { n: '04', label: 'Validate',   icon: Shield    },
  { n: '05', label: 'Dedup',      icon: GitMerge  },
  { n: '06', label: 'Priority',   icon: BarChart3 },
  { n: '07', label: 'Route',      icon: ArrowRight },
  { n: '08', label: 'Verify',     icon: Zap       },
]

export default function LandingPage() {
  const { isAuthenticated, user } = useAuthStore()

  const dashHref = user?.role === 'admin' ? '/admin' : user?.role === 'officer' ? '/officer' : '/dashboard'

  return (
    <PublicShell>
      {/* ── HERO ──────────────────────────────────────────── */}
      <section
        className="relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #0C1A2E 0%, #1E3A5F 60%, #1E4080 100%)' }}
        aria-labelledby="hero-heading"
      >
        {/* Grid overlay */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
          aria-hidden="true"
        />

        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
          {/* Status pill */}
          <div className="flex justify-center mb-6 sm:mb-8">
            <div className="inline-flex items-center gap-2 px-3.5 py-2 rounded-full bg-white/10 border border-white/20 text-xs text-white/80">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
              <span className="font-semibold">10 AI Agents Active</span>
              <span className="text-white/30 mx-1" aria-hidden="true">·</span>
              <span>LangGraph Supervisor Operational</span>
            </div>
          </div>

          {/* Headline */}
          <h1
            id="hero-heading"
            className="text-display text-white text-center mb-4 sm:mb-6"
            style={{ textShadow: '0 2px 20px rgba(0,0,0,0.3)' }}
          >
            Autonomous Civic Action,
            <br className="hidden sm:block" />
            <span className="text-sky-400"> Powered by AI</span>
          </h1>

          <p className="text-center text-white/70 text-base sm:text-lg max-w-2xl mx-auto mb-8 sm:mb-10 leading-relaxed px-2">
            From pothole to resolution — CivicFix AI uses a{' '}
            <strong className="text-white font-semibold">10-agent LangGraph supervisor</strong>{' '}
            to intelligently intake, classify, route, and verify civic complaints.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 px-4">
            {isAuthenticated ? (
              <>
                <Link to={dashHref} className="btn btn-accent btn-lg w-full sm:w-auto">
                  Go to Dashboard <ArrowRight size={18} aria-hidden="true" />
                </Link>
                <Link to="/report" className="btn btn-secondary btn-lg w-full sm:w-auto" style={{ background: 'rgba(255,255,255,0.1)', color: 'white', borderColor: 'rgba(255,255,255,0.2)' }}>
                  Report an Issue
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn btn-accent btn-lg w-full sm:w-auto">
                  Get Started — Free <ArrowRight size={18} aria-hidden="true" />
                </Link>
                <Link to="/login" className="btn btn-lg w-full sm:w-auto" style={{ background: 'rgba(255,255,255,0.1)', color: 'white', borderColor: 'rgba(255,255,255,0.2)' }}>
                  Sign In
                </Link>
              </>
            )}
          </div>

          {/* Trust row */}
          <div className="flex flex-wrap items-center justify-center gap-4 mt-8 sm:mt-10 text-xs text-white/50">
            {[
              { Icon: Shield, text: 'JWT + RBAC Secured' },
              { Icon: CheckCircle2, text: 'WCAG 2.1 AA' },
              { Icon: AlertTriangle, text: 'SLA Enforcement' },
            ].map(({ Icon, text }) => (
              <div key={text} className="flex items-center gap-1.5">
                <Icon size={13} aria-hidden="true" />
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PIPELINE STRIP ────────────────────────────────── */}
      <section className="bg-white border-y border-gray-200 py-6 overflow-hidden" aria-label="8-stage AI pipeline">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <p className="text-center text-xs font-mono font-semibold uppercase tracking-widest text-gray-400 mb-5">
            Autonomous 8-Stage Pipeline
          </p>
          <div className="flex items-center gap-0 overflow-x-auto pb-2 no-scrollbar justify-start sm:justify-center">
            {PIPELINE.map(({ n, label, icon: Icon }, idx) => (
              <div key={n} className="flex items-center gap-0 shrink-0">
                <div className="flex flex-col items-center gap-1.5 px-2 sm:px-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-900 flex items-center justify-center">
                    <Icon size={18} className="text-white" aria-hidden="true" />
                  </div>
                  <div className="text-center">
                    <div className="text-[10px] font-mono font-bold text-blue-900">{n}</div>
                    <div className="text-[11px] font-semibold text-gray-700 whitespace-nowrap">{label}</div>
                  </div>
                </div>
                {idx < PIPELINE.length - 1 && (
                  <ChevronRight size={16} className="text-gray-300 shrink-0 -mx-1" aria-hidden="true" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ─────────────────────────────────────────── */}
      <section className="py-12 sm:py-16 bg-gray-50" aria-label="Platform statistics">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {STATS.map(({ value, label, sub }) => (
              <div key={label} className="text-center">
                <div className="text-3xl sm:text-4xl font-black text-blue-900 font-mono leading-none mb-1">{value}</div>
                <div className="text-sm font-semibold text-gray-700 mb-0.5">{label}</div>
                <div className="text-xs text-gray-400">{sub}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ──────────────────────────────────────── */}
      <section className="py-12 sm:py-16 bg-white" aria-labelledby="features-heading">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10 sm:mb-12">
            <p className="section-label mb-2">Platform Capabilities</p>
            <h2 id="features-heading" className="text-heading-1 text-gray-900">
              Built for Real Civic Infrastructure
            </h2>
          </div>

          <div className="grid-3">
            {FEATURES.map(({ icon: Icon, title, desc, badge }) => (
              <div key={title} className="card p-5 sm:p-6 flex flex-col gap-3 card-hover">
                <div className="flex items-start justify-between gap-2">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center shrink-0" aria-hidden="true">
                    <Icon size={20} className="text-blue-700" />
                  </div>
                  {badge && (
                    <span className="badge badge-info font-mono">{badge}</span>
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-900 mb-1">{title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROLES ─────────────────────────────────────────── */}
      <section className="py-12 sm:py-16 bg-gray-50" aria-labelledby="portals-heading">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 id="portals-heading" className="text-heading-1 text-gray-900 mb-2">Three Portals. One Platform.</h2>
            <p className="text-gray-500 text-sm max-w-md mx-auto">Role-based access for citizens, field officers, and enterprise administrators.</p>
          </div>

          <div className="grid-3">
            {[
              {
                title: 'Citizen Portal',
                sub: 'For the Public',
                desc: 'Report civic issues via photo, voice, or text. Track AI processing and resolution status in real-time.',
                href: '/dashboard',
                btn: 'Open Citizen Portal',
                color: 'bg-blue-50 border-blue-100',
                icon: '🏙️',
              },
              {
                title: 'Officer Console',
                sub: 'Field Officers',
                desc: 'Manage SLA queue, dispatch crews, verify resolutions with AI-powered before/after comparison.',
                href: '/officer',
                btn: 'Officer Dashboard',
                color: 'bg-emerald-50 border-emerald-100',
                icon: '🛡️',
              },
              {
                title: 'Admin Hub',
                sub: 'Enterprise Admin',
                desc: 'RBAC management, department routing config, and real-time agent telemetry monitoring.',
                href: '/admin',
                btn: 'Admin Panel',
                color: 'bg-purple-50 border-purple-100',
                icon: '⚙️',
              },
            ].map((r) => (
              <div key={r.title} className={`card p-5 sm:p-6 border ${r.color} flex flex-col gap-4`}>
                <div>
                  <div className="text-3xl mb-3" aria-hidden="true">{r.icon}</div>
                  <div className="section-label mb-1">{r.sub}</div>
                  <h3 className="text-base font-bold text-gray-900 mb-2">{r.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{r.desc}</p>
                </div>
                <Link to={r.href} className="btn btn-primary btn-sm justify-center mt-auto">
                  {r.btn} <ArrowRight size={14} aria-hidden="true" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA SECTION ───────────────────────────────────── */}
      <section className="py-16 sm:py-20 bg-blue-900" aria-labelledby="cta-heading">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 id="cta-heading" className="text-display text-white mb-4">Ready to fix your city?</h2>
          <p className="text-white/70 text-base mb-8 leading-relaxed">
            Join citizens already using CivicFix AI to make local government accountable.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            {isAuthenticated ? (
              <Link to="/report" className="btn btn-accent btn-lg w-full sm:w-auto">
                Submit a Report <ArrowRight size={18} aria-hidden="true" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-accent btn-lg w-full sm:w-auto">
                  Create Account <ArrowRight size={18} aria-hidden="true" />
                </Link>
                <Link to="/login" className="btn btn-lg w-full sm:w-auto" style={{ background: 'rgba(255,255,255,0.1)', color: 'white', borderColor: 'rgba(255,255,255,0.2)' }}>
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>
    </PublicShell>
  )
}
