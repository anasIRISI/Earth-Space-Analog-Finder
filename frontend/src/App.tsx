import { Link, NavLink, Route, Routes } from 'react-router-dom'
import { backendOrigin } from './api/client'
import { useDiagnostics } from './hooks/useDiagnostics'

const modules = [
  { path: '/exploration', name: 'Exploration', phase: 2, title: 'Délimiter votre zone d’étude', description: 'Explorer Mars ou la Lune, dessiner et valider un polygone, puis consulter les caractéristiques disponibles.', detail: 'La prochaine étape intègre les premières données réelles et la sélection cartographique 2D.' },
  { path: '/recherche', name: 'Recherche', phase: 3, title: 'Trouver un terrain analogue', description: 'Comparer les caractéristiques disponibles selon un objectif : mobilité rover, habitat ou ressources ISRU.', detail: 'La recherche sera activée après la validation des jeux de données et du moteur de similarité.' },
  { path: '/resultats', name: 'Résultats', phase: 4, title: 'Examiner les sites candidats', description: 'Consulter le classement, localiser les sites sur Terre et comprendre les facteurs de similarité.', detail: 'Aucun résultat n’est encore calculé. Les scores seront produits à partir des caractéristiques documentées.' },
  { path: '/comparaison', name: 'Comparaison', phase: 4, title: 'Observer les régions côte à côte', description: 'Comparer la zone spatiale et le site terrestre en 2D, puis en 3D lorsque les données le permettent.', detail: 'CesiumJS et les fonds planétaires seront intégrés et vérifiés lors de la phase de visualisation.' },
  { path: '/rapport', name: 'Rapport', phase: 5, title: 'Documenter votre choix de site', description: 'Exporter un rapport PDF avec le tableau comparatif, les facteurs de similarité et les sources utilisées.', detail: 'Le rapport sera disponible après une analyse réelle et la sélection d’un site terrestre.' },
]

function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return <span aria-hidden="true">{diagonal ? '↗' : '→'}</span>
}

function PlanetDiagram() {
  return <div className="planet-diagram" aria-label="Illustration du rapprochement entre une zone spatiale et la Terre">
    <div className="diagram-grid" />
    <div className="orbit orbit-one" /><div className="orbit orbit-two" />
    <div className="planet mars"><div className="terrain terrain-one" /><div className="terrain terrain-two" /><div className="target"><span /></div></div>
    <span className="planet-label mars-label"><i /> MARS / LUNE<span>Zone d’étude</span></span>
    <svg className="transfer" viewBox="0 0 360 160" fill="none" aria-hidden="true"><path d="M16 22 C115 20 158 156 330 124" stroke="#a0aca3" strokeWidth="1" strokeDasharray="4 5" /><circle cx="330" cy="124" r="4" fill="#d6e6b8" /></svg>
    <div className="planet earth"><div className="land land-one" /><div className="land land-two" /><div className="land land-three" /><div className="earth-line" /></div>
    <span className="planet-label earth-label"><i /> TERRE<span>Sites analogues</span></span>
    <span className="diagram-caption">SCHÉMA DE PRINCIPE · PAS DE DONNÉES CARTOGRAPHIQUES</span>
  </div>
}

function SystemStatus() {
  const { health, readiness, loading, checkedAt, refresh } = useDiagnostics()
  return <section id="systeme" className="system-section scroll-mt-8">
    <div className="section-heading flex flex-wrap items-end justify-between gap-4">
      <div><p className="eyebrow">VOTRE ENVIRONNEMENT LOCAL</p><h2>Une base solide pour explorer.</h2></div>
      <button className="refresh-button" disabled={loading} onClick={refresh}><span aria-hidden="true" className={loading ? 'spin' : ''}>↻</span> {loading ? 'Vérification…' : 'Actualiser les services'}</button>
    </div>
    <div className="status-grid" aria-live="polite" aria-busy={loading}>
      <article className="status-card"><div className="flex items-center justify-between gap-3"><span className="service-icon" aria-hidden="true">⌘</span><StatusPill loading={loading} ok={!!health.data} /></div><h3>API Django</h3><p>{loading ? 'Connexion au backend en cours…' : health.data ? `Python ${health.data.python_version} · Django ${health.data.django_version}` : health.error}</p><code>/api/v1/health/</code></article>
      <article className="status-card"><div className="flex items-center justify-between gap-3"><span className="service-icon" aria-hidden="true">▤</span><StatusPill loading={loading} ok={!!readiness.data} /></div><h3>PostgreSQL + PostGIS</h3><p>{loading ? 'Vérification de l’extension spatiale…' : readiness.data ? `PostGIS ${readiness.data.postgis_version}` : readiness.error}</p><code>/api/v1/ready/</code></article>
      <article className="status-card data-card"><div className="flex items-center justify-between gap-3"><span className="service-icon" aria-hidden="true">◎</span><span className="pill planned">PHASE 2</span></div><h3>Données scientifiques</h3><p>Intégration à venir. Aucun jeu de données chargé et aucun score calculé.</p><span className="card-note">Des mesures traçables, des résultats explicables.</span></article>
    </div>
    <p className="last-check">{checkedAt ? `Dernière vérification à ${checkedAt.toLocaleTimeString('fr-FR')}.` : 'Les états des services sont vérifiés auprès du backend.'} Les diagnostics ne nécessitent aucun compte.</p>
  </section>
}

function StatusPill({ loading, ok }: { loading: boolean; ok: boolean }) {
  return <span className={`pill ${loading ? 'checking' : ok ? 'online' : 'offline'}`}><span aria-hidden="true">●</span> {loading ? 'VÉRIFICATION' : ok ? 'CONNECTÉ' : 'INDISPONIBLE'}</span>
}

function Home() {
  return <>
    <section className="hero">
      <div className="hero-copy"><div className="hero-eyebrow"><span className="tiny-cross" aria-hidden="true">✳</span> DE LA GÉOLOGIE À L’EXPLORATION SPATIALE</div><h1>Explorer ailleurs.<br />Tester <em>sur Terre.</em></h1><p>Relier les paysages de Mars et de la Lune aux terrains terrestres pour préparer les prochaines missions spatiales.</p><div className="hero-actions"><a className="button button-primary" href="#systeme">Vérifier l’environnement <Arrow /></a><a className="text-link" href={`${backendOrigin}/api/docs/`} target="_blank" rel="noreferrer">Documentation API <Arrow diagonal /></a></div><div className="hero-meta"><span>01 / 05</span><p>INITIALISATION DU PROJET<br /><strong>Infrastructure en cours de validation</strong></p></div></div>
      <PlanetDiagram />
    </section>
    <div className="principles flex flex-wrap justify-between gap-4"><span><i /> Sources scientifiques traçables</span><span><i /> Similarité explicable</span><span><i /> Mars · Lune · Terre</span><span><i /> Gratuit et open source</span></div>
    <SystemStatus />
    <section className="journey-section"><div className="section-heading"><p className="eyebrow">DU SITE CIBLE AU TERRAIN D’ESSAI</p><h2>Un parcours, cinq étapes.</h2><p className="section-description">Le développement avance progressivement. Les fonctions scientifiques seront activées après leur validation.</p></div><div className="journey-grid">{[
      ['01', 'Initialiser', 'Django, React et PostGIS. Connexions et environnement reproductible.', 'En cours', '/'],
      ['02', 'Cartographier', 'Données réelles, polygones et caractéristiques des zones.', 'Phase suivante', '/exploration'],
      ['03', 'Comparer', 'Normalisation, objectifs de test et classement des analogues.', 'À venir', '/recherche'],
      ['04', 'Visualiser', 'Résultats géolocalisés et comparaison des régions en 2D / 3D.', 'À venir', '/comparaison'],
      ['05', 'Documenter', 'Rapport PDF, sources, facteurs de similarité et recommandations.', 'À venir', '/rapport'],
    ].map(([number, title, description, state, path]) => <Link className={`journey-step ${number === '01' ? 'current' : ''}`} to={path} key={number}><span className="step-number">{number}<Arrow diagonal /></span><h3>{title}</h3><p>{description}</p><span className="step-state">{state}</span></Link>)}</div></section>
    <section className="next-section flex flex-wrap items-center justify-between gap-6"><div><p className="eyebrow">PROCHAINE ÉTAPE</p><h2>Donner une géographie aux données.</h2><p>Intégrer un premier jeu de données réel avant de lancer la recherche d’analogues.</p></div><Link className="button button-outline" to="/exploration">Découvrir la phase 2 <Arrow /></Link></section>
  </>
}

function PlannedPage({ module }: { module: typeof modules[number] }) {
  return <section className="planned-page"><p className="eyebrow">{module.name.toUpperCase()} · PHASE {module.phase}</p><span className="pill planned">FONCTIONNALITÉ À VENIR</span><h1>{module.title}</h1><p className="planned-description">{module.description}</p><div className="planned-detail"><span aria-hidden="true">◎</span><p>{module.detail}</p></div><p className="availability-note">La phase 1 prépare l’infrastructure. Aucun résultat scientifique n’est disponible à ce stade.</p><div className="hero-actions"><Link className="button button-primary" to="/">Retour à l’accueil <Arrow /></Link><a className="text-link" href={`${backendOrigin}/api/docs/`} target="_blank" rel="noreferrer">Consulter l’API <Arrow diagonal /></a></div></section>
}

export default function App() {
  return <div className="app-shell"><a className="skip-link" href="#main">Aller au contenu</a><header><div className="header-inner"><Link to="/" className="brand" aria-label="Earth-Space Analog Finder, accueil"><span className="brand-mark" aria-hidden="true"><span /></span><span>EARTH—SPACE<small>ANALOG FINDER</small></span></Link><nav aria-label="Navigation principale"><NavLink to="/" end>Accueil</NavLink>{modules.map((module) => <NavLink to={module.path} key={module.path}>{module.name}</NavLink>)}</nav><span className="header-badge"><i /> DÉVELOPPEMENT LOCAL</span></div></header><main id="main"><Routes><Route path="/" element={<Home />} />{modules.map((module) => <Route key={module.path} path={module.path} element={<PlannedPage module={module} />} />)}<Route path="*" element={<section className="planned-page"><p className="eyebrow">PAGE INTROUVABLE</p><h1>Cette trajectoire n’existe pas.</h1><Link className="button button-primary" to="/">Revenir à l’accueil <Arrow /></Link></section>} /></Routes></main><footer className="flex flex-wrap items-center justify-between gap-4"><p>EARTH—SPACE <span>ANALOG FINDER</span></p><p>Phase 1 · Infrastructure locale <span className="footer-dot">/</span> Les scores futurs seront des indicateurs de similarité.</p></footer></div>
}
