import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/projects": "http://localhost:8000",
      "/tasks": "http://localhost:8000"
    }
  }
});
