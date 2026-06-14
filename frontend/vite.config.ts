import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During `vite dev`, proxy API calls to the local FastAPI server
// (`kryptos serve`, default port 8000) so the SPA and API share an origin.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});
