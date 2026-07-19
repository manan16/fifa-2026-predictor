// Maps the seeded FIFA team codes to flagcdn.com codes. Most are plain
// ISO 3166-1 alpha-2; England has no ISO code of its own, so it uses
// flagcdn's non-ISO home-nation code instead.
const FIFA_TO_FLAGCDN: Record<string, string> = {
  ARG: "ar",
  FRA: "fr",
  ESP: "es",
  ENG: "gb-eng",
  BRA: "br",
  POR: "pt",
  NED: "nl",
  BEL: "be",
  GER: "de",
  CRO: "hr",
  MAR: "ma",
  SUI: "ch",
  JPN: "jp",
  USA: "us",
  AUT: "at",
  SWE: "se",
  SEN: "sn",
  COL: "co",
  ECU: "ec",
  CAN: "ca",
  AUS: "au",
  PAR: "py",
  CIV: "ci",
  NOR: "no",
  ALG: "dz",
  MEX: "mx",
  EGY: "eg",
  RSA: "za",
  COD: "cd",
  CPV: "cv",
  BIH: "ba",
  GHA: "gh",
};

/**
 * flagcdn.com flag image URL for a FIFA team code, or null if the code is
 * missing/unmapped (e.g. a "TBD" slot) — callers should fall back to text.
 */
export function flagUrl(code: string | null | undefined, width: 40 | 80 | 160 = 80): string | null {
  if (!code) return null;
  const flagCode = FIFA_TO_FLAGCDN[code.toUpperCase()];
  if (!flagCode) return null;
  return `https://flagcdn.com/w${width}/${flagCode}.png`;
}