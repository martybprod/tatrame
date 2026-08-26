/*
 * icones-zodiaque.jsx — Ta Trame
 * Les 12 glyphes zodiacaux, en remplacement des caractères Unicode ♈…♓.
 *
 * Même grammaire visuelle que icones-trame.jsx :
 *   viewBox 0 0 24 24 · trait 1.5 currentColor · bouts et jointures arrondis
 *   disques pleins = nœuds (point de nouage ou de croisement des fils)
 *
 * Principe : le tracé canonique du glyphe est conservé intégralement — la
 * lisibilité du signe prime. Le tissage entre par accent : trait continu lu
 * comme un fil, nœud au point de tension, fils de trame dans les formes
 * fermées (Taureau).
 *
 * À fusionner dans l'objet TOUTES de icones-trame.jsx :
 *   import { ICONES_ZODIAQUE } from './icones-zodiaque';
 *   const TOUTES = { ...ICONES_NAV, ...ICONES_JOUR, ...ICONES_DOM, ...ICONES_ZODIAQUE };
 */

const Noeud = ({ cx, cy, r = 1.2 }) => (
  <circle cx={cx} cy={cy} r={r} fill="currentColor" stroke="none" />
);

export const ICONES_ZODIAQUE = {
  /* ♈ Bélier — deux fils qui s'enroulent vers l'extérieur, noués sur la tige. */
  belier: (
    <>
      <path d="M12 20.5V10" />
      <path d="M12 10C12 5 8.5 3 6 4.5 3.6 6 3.8 9.5 6 10.5" />
      <path d="M12 10c0-5 3.5-7 6-5.5 2.4 1.5 2.2 5 0 6" />
      <Noeud cx="12" cy="10" />
    </>
  ),

  /* ♉ Taureau — le disque reçoit deux fils de trame, les cornes se nouent au sommet. */
  taureau: (
    <>
      <circle cx="12" cy="15" r="5" />
      <path d="M6 11C5.2 5.5 9 3.5 12 7c3-3.5 6.8-1.5 6 4" />
      <path d="M7.7 13.5h8.6M7.7 16.5h8.6" />
      <Noeud cx="12" cy="7" r={1.1} />
    </>
  ),

  /* ♊ Gémeaux — deux fils de chaîne tenus par une trame haut et bas. Quatre nœuds. */
  gemeaux: (
    <>
      <path d="M6 5c3-1.5 9-1.5 12 0" />
      <path d="M6 19c3 1.5 9 1.5 12 0" />
      <path d="M9 4.3v15.4M15 4.3v15.4" />
      <Noeud cx="9" cy="4.5" r={0.95} />
      <Noeud cx="15" cy="4.5" r={0.95} />
      <Noeud cx="9" cy="19.5" r={0.95} />
      <Noeud cx="15" cy="19.5" r={0.95} />
    </>
  ),

  /* ♋ Cancer — les deux boucles deviennent des pelotes de fil. */
  cancer: (
    <>
      <path d="M4 14.5C4.5 7.5 9.5 5 15.5 6.2" />
      <circle cx="18" cy="7.5" r="2.6" />
      <path d="M20 9.5c-.5 7-5.5 9.5-11.5 8.3" />
      <circle cx="6" cy="16.5" r="2.6" />
      <Noeud cx="18" cy="7.5" r={1} />
      <Noeud cx="6" cy="16.5" r={1} />
    </>
  ),

  /* ♌ Lion — un seul fil déroulé depuis la pelote. */
  lion: (
    <>
      <circle cx="7" cy="16.5" r="3.2" />
      <path d="M9.5 14.6C12 11 10.5 6 13.5 4.6c3.3-1.5 6 1 4.9 3.9-.8 2.1-2.9 3-3.9 4.5-1 1.6.3 3.5 2.5 4 1.7.4 3 0 3.8-.7" />
      <Noeud cx="7" cy="16.5" r={1.1} />
    </>
  ),

  /* ♍ Vierge — le nœud marque le croisement de la boucle sur la troisième jambe.
     Reste dense sous 20 px : prévoir une variante allégée si affichage réduit. */
  vierge: (
    <>
      <path d="M4 20.5V9.5" />
      <path d="M4 9.5C4 6.5 8.2 6.5 8.2 9.5" />
      <path d="M8.2 9.5V20.5" />
      <path d="M8.2 9.5c0-3 4.2-3 4.2 0" />
      <path d="M12.4 9.5v7C12.4 19.5 15.5 20.8 17.8 19" />
      <path d="M10.8 15.2c3.2.6 6.7 2.3 8.7 5.6" />
      <Noeud cx="12.4" cy="15.6" r={1} />
    </>
  ),

  /* ♎ Balance — un fil tendu, un fil qui se soulève. Nœud au sommet. */
  balance: (
    <>
      <path d="M3 18h18" />
      <path d="M4.5 13.5h4a3.5 3.5 0 0 1 7 0h4" />
      <Noeud cx="12" cy="10" r={1.1} />
    </>
  ),

  /* ♏ Scorpion — même montage que la Vierge, le fil se termine en pointe. */
  scorpion: (
    <>
      <path d="M4 20.5V9.5" />
      <path d="M4 9.5C4 6.5 8.2 6.5 8.2 9.5" />
      <path d="M8.2 9.5V20.5" />
      <path d="M8.2 9.5c0-3 4.2-3 4.2 0" />
      <path d="M12.4 9.5v7c0 3 2.6 4 5.1 2l2.8-2.8" />
      <path d="M20.3 15.7h-3.7M20.3 15.7v3.7" />
    </>
  ),

  /* ♐ Sagittaire — deux fils qui se croisent, nœud à l'intersection. */
  sagittaire: (
    <>
      <path d="M4.5 19.5 19 5" />
      <path d="M19 5h-5.5M19 5v5.5" />
      <path d="M7.5 10.5 13.5 16.5" />
      <Noeud cx="10.5" cy="13.5" r={1.1} />
    </>
  ),

  /* ♑ Capricorne — le fil descend puis forme une boucle refermée sur elle-même. */
  capricorne: (
    <>
      <path d="M4 9c1.5-3 5-2.5 6 1 .7 2.5 1 4.5 1.5 6.5" />
      <path d="M11.5 16.5c1 3 4.5 4 6.5 1.5s.5-6-2.5-5.8c-1.7.1-2.5 1.6-2 2.8" />
      <Noeud cx="11.5" cy="16.5" r={1} />
    </>
  ),

  /* ♒ Verseau — les chevrons doubles sont déjà un motif de sergé. Inchangé. */
  verseau: (
    <>
      <path d="M3.5 10 7.5 7l4 3 4-3 4 3" />
      <path d="M3.5 17 7.5 14l4 3 4-3 4 3" />
    </>
  ),

  /* ♓ Poissons — deux navettes dos à dos, reliées par un fil de trame. */
  poissons: (
    <>
      <path d="M8 4C4.5 8 4.5 16 8 20" />
      <path d="M16 4c3.5 4 3.5 12 0 16" />
      <path d="M5.4 12h13.2" />
      <Noeud cx="12" cy="12" />
    </>
  ),
};

/* Ordre zodiacal, pratique pour les boucles d'affichage. */
export const ORDRE_ZODIAQUE = [
  'belier',
  'taureau',
  'gemeaux',
  'cancer',
  'lion',
  'vierge',
  'balance',
  'scorpion',
  'sagittaire',
  'capricorne',
  'verseau',
  'poissons',
];

/* Libellés affichables, si tu remplaces aussi les caractères Unicode dans le texte. */
export const NOMS_ZODIAQUE = {
  belier: 'Bélier',
  taureau: 'Taureau',
  gemeaux: 'Gémeaux',
  cancer: 'Cancer',
  lion: 'Lion',
  vierge: 'Vierge',
  balance: 'Balance',
  scorpion: 'Scorpion',
  sagittaire: 'Sagittaire',
  capricorne: 'Capricorne',
  verseau: 'Verseau',
  poissons: 'Poissons',
};

export default ICONES_ZODIAQUE;
