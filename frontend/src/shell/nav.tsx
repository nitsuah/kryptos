import { createContext, useContext } from "react";

// Lets a module jump to another one (e.g. Overview's "open fronts" → Ledger)
// without knowing how the carousel is implemented.
export interface Nav {
  go: (moduleId: string) => void;
}

export const NavContext = createContext<Nav>({ go: () => undefined });

export function useNav(): Nav {
  return useContext(NavContext);
}
