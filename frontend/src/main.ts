import { createApp } from "vue";
import { createI18n } from "vue-i18n";
import App from "./App.vue";
import zhCN from "./locales/zh-CN";
import enUS from "./locales/en-US";
import "./styles/main.css";

const savedLocale = localStorage.getItem("easysudoku.locale") || "";
const browserLocale = navigator.language.toLowerCase().startsWith("zh") ? "zh-CN" : "en-US";

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale || browserLocale,
  fallbackLocale: "en-US",
  messages: {
    "zh-CN": zhCN,
    "en-US": enUS
  }
});

createApp(App).use(i18n).mount("#app");
