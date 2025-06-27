import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // everything beginning with these paths is forwarded to the API
      "/wizard": "http://localhost:8000",
      "/projects": "http://localhost:8000",
      "/tasks": "http://localhost:8000",
      "/ws": {
        target: "ws://localhost:8000",
        ws: true
      }
    }
  }
});
