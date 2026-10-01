import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, forward API calls to the Flask server running on port 5000.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:5000" } },
});
