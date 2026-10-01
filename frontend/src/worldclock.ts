// Weltzeituhr (Urania World Clock, Alexanderplatz) panels for the dashboard.
//
// The real clock is a 24-sided drum: each face is one hour zone, engraved
// with city names, and a ring of hour numbers turns beneath it. The names
// below are the plate names read off photographs of the clock
// (src/kryptos/k4/world_clock_cities.py, 130 of 146 read), spelled as
// engraved. They are grouped here by each city's standard UTC offset;
// the drum's exact plate-to-face layout is only partly recorded, so the
// grouping is an approximation, not a transcription. Faces with no read
// plates are left blank, as in the photos.

export interface ClockFace {
  offset: number; // standard UTC offset of the face, in hours
  cities: string[];
}

export const WORLD_CLOCK_FACES: ClockFace[] = [
  { offset: -11, cities: ["APIA"] },
  { offset: -10, cities: ["HONOLULU", "MARQUESAS I."] },
  { offset: -9, cities: ["NOME", "FAIRBANKS", "ANCHORAGE"] },
  { offset: -8, cities: ["VANCOUVER", "DAWSON", "SAN FRANCISCO", "LOS ANGELES"] },
  { offset: -7, cities: ["EDMONTON", "DENVER"] },
  { offset: -6, cities: ["NEW ORLEANS", "MEXIKO-STADT"] },
  { offset: -5, cities: [] },
  { offset: -4, cities: ["HALIFAX", "CARACAS", "LA PAZ", "ASUNCION", "SANTIAGO DE CHILE"] },
  { offset: -3, cities: ["WESTGRÖNLAND", "BRASILIA", "RIO DE JANEIRO", "SAO PAULO", "MONTEVIDEO", "BUENOS AIRES"] },
  { offset: -2, cities: [] },
  { offset: -1, cities: ["OSTGRÖNLAND", "AZOREN", "KAPVERDE"] },
  {
    offset: 0,
    cities: ["REYKJAVIK", "DUBLIN", "LONDON", "LISSABON", "MADEIRA", "CASABLANCA", "DAKAR", "BAMAKO", "ACCRA"],
  },
  {
    offset: 1,
    cities: [
      "BERLIN",
      "OSLO",
      "KOPENHAGEN",
      "STOCKHOLM",
      "AMSTERDAM",
      "BRÜSSEL",
      "PARIS",
      "MADRID",
      "BERN",
      "ROM",
      "WIEN",
      "PRAG",
      "WARSCHAU",
      "BUDAPEST",
      "PRESSBURG",
      "BELGRAD",
      "TUNIS",
      "KINSHASA",
    ],
  },
  {
    offset: 2,
    cities: [
      "HELSINKI",
      "RIGA",
      "TALLINN",
      "WILNA",
      "MINSK",
      "KIEW",
      "BUKAREST",
      "SOFIA",
      "ATHEN",
      "ISTANBUL",
      "ANKARA",
      "NIKOSIA",
      "BEIRUT",
      "DAMASKUS",
      "TEL AVIV",
      "JERUSALEM",
      "KAPSTADT",
    ],
  },
  {
    offset: 3,
    cities: ["MURMANSK", "ST. PETERSBURG", "MOSKAU", "BAGDAD", "ADEN", "SANAA", "ADDIS ABEBA", "MOGADISCHU", "DAR ES SALAAM", "ANTANANARIVO", "TEHERAN"],
  },
  { offset: 4, cities: ["NISCHNIJ NOWGOROD", "WOLGOGRAD", "BAKU", "TIFLIS", "ERIWAN", "MAURITIUS", "KABUL"] },
  { offset: 5, cities: ["JEKATERINBURG", "ASCHGABAT", "DUSCHANBE", "KARACHI", "NEW DELHI", "COLOMBO"] },
  { offset: 6, cities: ["OMSK", "BISCHKEK", "ALMATY", "TASCHKENT", "NOWOSIBIRSK", "DHAKA", "RANGUN"] },
  { offset: 7, cities: ["KRASNOJARSK", "HANOI", "BANGKOK", "PHNOM PENH", "JAKARTA"] },
  { offset: 8, cities: ["PEKING", "SHANGHAI", "HONGKONG", "MANILA", "KUALA LUMPUR", "SINGAPUR", "PERTH"] },
  { offset: 9, cities: ["PJÖNGJANG", "SEOUL", "TOKYO"] },
  { offset: 10, cities: [] },
  { offset: 11, cities: ["MAGADAN", "SACHALIN"] },
  { offset: 12, cities: ["KAMTSCHATKA", "KAP DESCHNEW", "WELLINGTON", "DATUMSGRENZE"] },
];

export const BERLIN_FACE = WORLD_CLOCK_FACES.findIndex((f) => f.offset === 1);

/** Hour (0–23) on a face's standard-time offset for a UTC instant. */
export function faceHour(now: Date, offset: number): number {
  return (((now.getUTCHours() + offset) % 24) + 24) % 24;
}

export function offsetLabel(offset: number): string {
  if (offset === 0) return "UTC";
  return `UTC${offset > 0 ? "+" : "−"}${Math.abs(offset)}`;
}
