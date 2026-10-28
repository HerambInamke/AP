import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // strictPort: the API only allows this origin (CORS_ORIGINS); silently moving to 5174 breaks login
  server: { port: 5173, strictPort: true },
});
