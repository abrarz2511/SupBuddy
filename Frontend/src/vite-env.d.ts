/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_REFRESH_INTERVAL: string;
  readonly VITE_ALERT_REFRESH_INTERVAL: string;
  readonly VITE_SHIPMENT_REFRESH_INTERVAL: string;
  readonly VITE_ENABLE_AUTO_REFRESH: string;
  readonly VITE_ENABLE_WEBSOCKET: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Made with Bob
