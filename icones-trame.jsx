/*
 * icones-trame.jsx — Ta Trame
 * Jeu d'icônes unifié autour du vocabulaire du tissage.
 *
 * Grammaire visuelle
 *   viewBox    : 0 0 24 24
 *   trait      : 1.5 (currentColor), bouts et jointures arrondis
 *   accents    : petits disques pleins = nœuds / points de croisement
 *   exception  : `domine` utilise un trait de 2.4 sur le fil dominant
 *
 * Les définitions ci-dessous ne contiennent QUE le contenu interne du <svg>.
 * Le composant <Icone> fournit l'enveloppe et les attributs communs.
 */

const ENVELOPPE = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

/* Nœud : petit disque plein, réutilisé partout comme accent. */
const Noeud = ({ cx, cy, r = 1.3 }) => (
  <circle cx={cx} cy={cy} r={r} fill="currentColor" stroke="none" />
);

/* ------------------------------------------------------------------ */
/* Navigation                                                          */
/* ------------------------------------------------------------------ */

export const ICONES_NAV = {
  /* Rosace de fils rayonnants : la chaîne part du centre, une trame la traverse. */
  jour: (
    <>
      <circle cx="12" cy="12" r="4.5" />
      <path d="M8.1 10.4H15.9M8.1 13.6H15.9" />
      <path d="M12 2.8V5M12 19v2.2M2.8 12H5M19 12h2.2M5.5 5.5l1.55 1.55M16.95 16.95l1.55 1.55M18.5 5.5l-1.55 1.55M7.05 16.95L5.5 18.5" />
    </>
  ),

  /* Navette-œil : la forme de la navette est celle de l'œil, le fil la traverse. */
  apercu: (
    <>
      <path d="M3.2 12C6.6 6.6 17.4 6.6 20.8 12c-3.4 5.4-14.2 5.4-17.6 0Z" />
      <path d="M3.2 12H1.2M20.8 12h2" />
      <circle cx="12" cy="12" r="2.3" />
      <Noeud cx="12" cy="12" r={0.9} />
    </>
  ),

  /* Silhouette tissée : tête nouée, torse en chaîne et trame. */
  portrait: (
    <>
      <circle cx="12" cy="6" r="3" />
      <path d="M8 12h8M8 12l-1 8.5M12 12v8.5M16 12l1 8.5" />
      <path d="M7.5 15.4h9M7.2 18h9.6" />
    </>
  ),

  /* Constellation : nœuds reliés par un fil unique. */
  ciel: (
    <>
      <path d="M4.5 17.5L9 9.5l6 3.5 4.5-7.5M15 13l-2 7" />
      <Noeud cx="4.5" cy="17.5" r={1.1} />
      <Noeud cx="9" cy="9.5" r={1.1} />
      <Noeud cx="15" cy="13" r={1.1} />
      <Noeud cx="19.5" cy="5.5" r={1.1} />
      <Noeud cx="13" cy="20" r={1.1} />
    </>
  ),

  /* Rouleau d'étoffe : le parchemin devient pièce de tissu enroulée. */
  regles: (
    <>
      <circle cx="7" cy="12" r="4" />
      <path d="M7 9.6a2.4 2.4 0 1 1-2.4 2.4" />
      <path d="M7 8h13M7 16h13" />
      <path d="M20 8c1.2 1.3-1.2 2.7 0 4s-1.2 2.7 0 4" />
      <path d="M11.5 8v8M15.5 8v8" />
    </>
  ),
};

/* ------------------------------------------------------------------ */
/* Du jour                                                             */
/* ------------------------------------------------------------------ */

export const ICONES_JOUR = {
  /* Le fil du jour : une ondulation, un nœud au centre. */
  fil: (
    <>
      <path d="M3 16c3 0 3-8 6-8s3 8 6 8 3-8 6-8" />
      <Noeud cx="12" cy="12" />
    </>
  ),

  /* Fil dominant : trois fils parallèles, celui du milieu marqué.
     En dessous de 20 px, préférer l'opacité seule au trait épaissi. */
  domine: (
    <>
      <path d="M2.5 7C6 4 8 10 12 7c4-3 6 3 9.5 0" opacity="0.55" />
      <path d="M2.5 17C6 14 8 20 12 17c4-3 6 3 9.5 0" opacity="0.55" />
      <path d="M2.5 12C6 9 8 15 12 12c4-3 6 3 9.5 0" strokeWidth="2.4" />
      <Noeud cx="12" cy="12" />
    </>
  ),

  /* Croissant tramé : la lune traversée de fils de trame. */
  lune_maison: (
    <>
      <path d="M18.3 5.6a9 9 0 1 0 0 12.8 7 7 0 1 1 0-12.8Z" />
      <path d="M4.6 8h4.6M4 12h4.5M4.6 16h4.6" />
    </>
  ),

  /* Moitié tissée : le cercle mi-rempli de trame, mi-vide. */
  phase: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 3.5v17" />
      <path d="M5.6 7H12M4.2 9.5H12M3.5 12H12M4.2 14.5H12M5.6 17H12" />
    </>
  ),

  /* Nuance : dégradé de densité de la trame, serré vers lâche. */
  nuance: <path d="M3 5v14M4.2 5v14M5.8 5v14M8 5v14M11 5v14M15 5v14M20.5 5v14" />,

  /* Cycle : fil enroulé sur lui-même autour d'un centre. */
  cycle: (
    <>
      <path d="M12 5a7 7 0 1 1-7 7" />
      <path d="M12 8.5a3.5 3.5 0 1 1-3.5 3.5" />
      <Noeud cx="12" cy="12" r={1.2} />
    </>
  ),

  /* Rappel : le nœud fait au fil pour ne pas oublier. */
  rappel: (
    <>
      <path d="M2.5 15c5.5 0 7-6.5 11.5-5.5 3 .7 2.5 5-1 5" />
      <path d="M21.5 15c-5.5 0-7-6.5-11.5-5.5-3 .7-2.5 5 1 5" />
    </>
  ),
};

/* ------------------------------------------------------------------ */
/* Domaines (12 maisons)                                               */
/* ------------------------------------------------------------------ */

export const ICONES_DOM = {
  /* Toi : le point unique où chaîne et trame se croisent. */
  soi: (
    <>
      <path d="M12 3v18M3 12h18" />
      <circle cx="12" cy="12" r="3.5" />
      <Noeud cx="12" cy="12" />
    </>
  ),

  /* Argent : la bobine, réserve de fil. */
  ressources: (
    <>
      <path d="M7 4h10M7 20h10" />
      <path d="M9 4c-1.5 4-1.5 12 0 16M15 4c1.5 4 1.5 12 0 16" />
      <path d="M8.3 9.5h7.4M8 12h8M8.3 14.5h7.4" />
    </>
  ),

  /* Mots : deux fils qui se croisent et repartent chacun de son côté. */
  echanges: (
    <>
      <path d="M3 6c6 0 12 12 18 12M3 18c6 0 12-12 18-12" />
      <Noeud cx="12" cy="12" />
    </>
  ),

  /* Famille : des fils issus d'un même nœud, liés par une trame. */
  racines: (
    <>
      <circle cx="12" cy="4.5" r="2" />
      <path d="M12 6.5v4.5" />
      <path d="M12 11c0 3-3 4-4 6-.8 1.6-1 2.5-1 3.5M12 11v9.5M12 11c0 3 3 4 4 6 .8 1.6 1 2.5 1 3.5" />
      <path d="M8.8 15.6c1.7-.8 4.7-.8 6.4 0" />
    </>
  ),

  /* Créativité : la navette en mouvement trace un motif. */
  creation: (
    <>
      <path d="M3.2 18.5c1.3-1.9 4.3-1.9 5.6 0-1.3 1.9-4.3 1.9-5.6 0Z" />
      <path d="M8.8 18.5c3.2 0 3.2-4.5 6.2-4.5s3-5 6-5" />
      <path d="M19 2.5v3M17.5 4h3" />
    </>
  ),

  /* Habitudes : l'armure toile, le motif le plus régulier qui soit. */
  quotidien: <path d="M8 4v16M12 4v16M16 4v16M4 8h16M4 12h16M4 16h16" />,

  /* Sens : le droit fil, tout converge vers un point. */
  sens: (
    <>
      <path d="M3 5c7 2 11 6 16.5 7M3 10c6 1 11 1.5 16.5 2M3 14c6-1 11-1.5 16.5-2M3 19c7-2 11-6 16.5-7" />
      <Noeud cx="20" cy="12" r={1.4} />
    </>
  ),

  /* Métier : le métier à tisser, cadre et chaîne montée. */
  metier: (
    <>
      <path d="M4 4v16M20 4v16M3 6h18M3 18h18" />
      <path d="M8 6v12M12 6v12M16 6v12" />
      <path d="M4 13h16" strokeWidth="2.4" />
    </>
  ),

  /* Communauté : trois brins tressés, indissociables. */
  communaute: (
    <>
      <path d="M8 3c0 3 8 3 8 6s-8 3-8 6 8 3 8 6" />
      <path d="M16 3c0 3-8 3-8 6s8 3 8 6-8 3-8 6" />
      <path d="M12 3v18" />
    </>
  ),

  /* Solitude : un fil qui se retire de la nappe. */
  retrait: (
    <>
      <path d="M14 4v16M17 4v16M20 4v16" />
      <path d="M11 4c0 5-6 6-6.5 11-.2 2 0 3.5.5 5" />
    </>
  ),

  /* Traversées : la navette passe d'un bord à l'autre de la chaîne. */
  traversee: (
    <>
      <path d="M5 3v6.5M9 3v6.5M15 3v6.5M19 3v6.5M5 14.5V21M9 14.5V21M15 14.5V21M19 14.5V21" />
      <path d="M7 12c2-2.4 8-2.4 10 0-2 2.4-8 2.4-10 0Z" />
      <path d="M7 12H2.6M17 12h4.4" />
    </>
  ),

  /* Couple : deux fils torsadés l'un autour de l'autre. */
  autre: (
    <>
      <path d="M9 3c0 4.5 6 5.5 6 9s-6 4.5-6 9" />
      <path d="M15 3c0 4.5-6 5.5-6 9s6 4.5 6 9" />
    </>
  ),
};

/* ------------------------------------------------------------------ */
/* Composant                                                           */
/* ------------------------------------------------------------------ */

const TOUTES = { ...ICONES_NAV, ...ICONES_JOUR, ...ICONES_DOM };

/**
 * <Icone nom="metier" taille={24} />
 * La couleur suit `currentColor` : elle s'hérite du parent.
 * `titre` rend l'icône accessible ; sans lui elle est masquée aux lecteurs d'écran.
 */
export function Icone({ nom, taille = 24, titre, ...props }) {
  const contenu = TOUTES[nom];
  if (!contenu) return null;

  return (
    <svg
      {...ENVELOPPE}
      width={taille}
      height={taille}
      role={titre ? 'img' : undefined}
      aria-label={titre}
      aria-hidden={titre ? undefined : true}
      {...props}
    >
      {contenu}
    </svg>
  );
}

export default Icone;
