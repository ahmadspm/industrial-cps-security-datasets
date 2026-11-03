import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/industrial-cps-security-datasets/",
  plugins: [react()],
  build: {
    outDir: "github-dist",
    emptyOutDir: true,
    sourcemap: false,
  },
});
