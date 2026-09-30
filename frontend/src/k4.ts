// K4 constants shared by the dashboard. Crib positions are 0-indexed,
// end-exclusive, and match kryptos.k4.keystream_validator.K4_CRIBS
// (EAST 21–24, NORTHEAST 25–33, BERLIN 63–68, CLOCK 69–73).

export const K4 =
  "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR";

export interface Crib {
  label: string;
  plain: string;
  start: number;
  end: number; // exclusive
  released: string;
  tone: "a" | "b" | "c" | "d";
}

export const CRIBS: Crib[] = [
  { label: "EAST", plain: "EAST", start: 21, end: 25, released: "Aug 2020", tone: "a" },
  { label: "NORTHEAST", plain: "NORTHEAST", start: 25, end: 34, released: "Jan 2020", tone: "b" },
  { label: "BERLIN", plain: "BERLIN", start: 63, end: 69, released: "Nov 2010", tone: "c" },
  { label: "CLOCK", plain: "CLOCK", start: 69, end: 74, released: "Nov 2014", tone: "d" },
];

export function cribAt(pos: number): Crib | null {
  return CRIBS.find((c) => pos >= c.start && pos < c.end) ?? null;
}

export const TIER_LABEL: Record<string, string> = {
  eliminated: "Eliminated",
  statistical: "Statistical",
  sampled_null: "Sampled null",
  open: "Open",
};

export const TIER_HINT: Record<string, string> = {
  eliminated: "No key in the stated range fits the 24 crib letters; the check ships a positive control.",
  statistical: "Compared against shuffled-ciphertext controls; K4 looks like the controls.",
  sampled_null: "Specific keys or settings were tried and failed; the family as a whole is not ruled out.",
  open: "Not yet tested in a way that settles anything.",
};
