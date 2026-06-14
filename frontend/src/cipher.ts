// Client-side reimplementations of the solved-section ciphers, mirroring
// kryptos.ciphers exactly, so the Decode page can animate each step without a
// round-trip. Verified against the canonical K1/K2/K3 plaintexts.

export const KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ";

export interface SubStep {
  cipher: string;
  key: string;
  plain: string;
  cipherIdx: number;
  keyIdx: number;
  plainIdx: number;
}

/** Build a keyword-mixed alphabet (KRYPTOS -> KRYPTOSABCDEFGHIJLMNQUVWXZ). */
export function keyedAlphabet(keyword: string): string {
  const base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const seen: string[] = [];
  for (const ch of (keyword + base).toUpperCase()) {
    if (base.includes(ch) && !seen.includes(ch)) seen.push(ch);
  }
  return seen.join("");
}

/**
 * Keyed-alphabet Vigenère decryption (K1/K2 method): for each cipher letter,
 * P = KEYED[(KEYED.index(C) - KEYED.index(K)) mod 26]. Returns per-letter steps.
 */
export function vigenereSteps(ciphertext: string, key: string): SubStep[] {
  const cleanKey = key.toUpperCase().replace(/[^A-Z]/g, "");
  const steps: SubStep[] = [];
  let ki = 0;
  for (const raw of ciphertext.toUpperCase()) {
    if (raw < "A" || raw > "Z") continue;
    const k = cleanKey[ki % cleanKey.length];
    const cipherIdx = KEYED_ALPHABET.indexOf(raw);
    const keyIdx = KEYED_ALPHABET.indexOf(k);
    const plainIdx = (((cipherIdx - keyIdx) % 26) + 26) % 26;
    steps.push({ cipher: raw, key: k, plain: KEYED_ALPHABET[plainIdx], cipherIdx, keyIdx, plainIdx });
    ki += 1;
  }
  return steps;
}

export function decodeVigenere(ciphertext: string, key: string): string {
  return vigenereSteps(ciphertext, key)
    .map((s) => s.plain)
    .join("");
}

export type Grid = string[][];

/** Rows of `cols` chars (last row padded with spaces). */
export function toGrid(text: string, cols: number): Grid {
  const rows = Math.ceil(text.length / cols);
  const g: Grid = [];
  let idx = 0;
  for (let r = 0; r < rows; r++) {
    const row: string[] = [];
    for (let c = 0; c < cols; c++) row.push(idx < text.length ? text[idx++] : " ");
    g.push(row);
  }
  return g;
}

/** Rotate a grid 90° clockwise — mirrors kryptos.ciphers._rotate_right. */
export function rotateRight(g: Grid): Grid {
  const rows = g.length;
  if (rows === 0) return [];
  const cols = g[0].length;
  const out: Grid = [];
  for (let c = 0; c < cols; c++) {
    const row: string[] = [];
    for (let r = rows - 1; r >= 0; r--) row.push(g[r][c]);
    out.push(row);
  }
  return out;
}

export function gridToText(g: Grid): string {
  return g.map((row) => row.join("")).join("");
}

export interface K3Stage {
  label: string;
  grid: Grid;
}

/**
 * K3 double rotational transposition stages (24×14 fill → 90cw → reshape to 8
 * cols → 90cw), mirroring kryptos.ciphers.double_rotational_transposition.
 */
export function k3Stages(ciphertext: string): K3Stage[] {
  const clean = ciphertext.replace(/\s/g, "").replace(/^\?/, "");
  const m1 = toGrid(clean, 24);
  const m2 = rotateRight(m1);
  const t1 = gridToText(m2);
  const m3 = toGrid(t1, 8);
  const m4 = rotateRight(m3);
  return [
    { label: "1 · Fill 24-column grid (14 rows)", grid: m1 },
    { label: "2 · Rotate 90° clockwise", grid: m2 },
    { label: "3 · Reshape to 8 columns", grid: m3 },
    { label: "4 · Rotate 90° clockwise → plaintext", grid: m4 },
  ];
}

export function decodeK3(ciphertext: string): string {
  const stages = k3Stages(ciphertext);
  return gridToText(stages[stages.length - 1].grid).replace(/\s+$/, "");
}

// Canonical solved-section inputs (public Kryptos data, from config/config.json).
// Spaces and `?` markers are stripped by the decode functions above.
export const SECTION_DATA = {
  K1: {
    cipher: "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD",
    key: "PALIMPSEST",
    note: "Vigenère with the KRYPTOS-keyed alphabet. Watch for the deliberate misspelling IQLUSION.",
  },
  K2: {
    cipher:
      "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE GGWHKK?DQMCPFQZDQMMIAGPFXHQRLG " +
      "TIMVMZJANQLVKQEDAGDVFRPJUNGEUNA QZGZLECGYUXUEENJTBJLBQCRTBJDFHRR " +
      "YIZETKZEMVDUFKSJHKFWHKUWQLSZFTI HHDDDUVH?DWKBFUFPWNTDFIYCUQZERE " +
      "EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDX FLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKF " +
      "FHQNTGPUAECNUVPDJMQCLQUMUNEDFQ ELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE " +
      "DNQFMPNZGLFLPMRJQYALMGNUVPDXVKP DQUMEBEDMHDAFMJGZNUPLGESWJLLAETG",
    key: "ABSCISSA",
    note: "Same method as K1. The ? marks are structural nulls, not part of the message.",
  },
  K3: {
    cipher:
      "?ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNE" +
      "TPRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOL" +
      "SEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWENATAMATEGYEERLBTEEFOAS" +
      "FIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAECTDDHIL" +
      "CEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIME" +
      "HNLSSTTRTVDOHW",
    key: null,
    note: "Double rotational transposition — no substitution. Reveals DESPARATLY (sic).",
  },
} as const;
