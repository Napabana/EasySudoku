import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/upload": "http://127.0.0.1:8000",
      "/next-step": "http://127.0.0.1:8000",
      "/hint-cell": "http://127.0.0.1:8000",
      "/solve": "http://127.0.0.1:8000"
    }
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
