import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { TonConnectUIProvider } from "@tonconnect/ui-react";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { GalleryPage } from "./pages/GalleryPage";
import { RunDetailPage } from "./pages/RunDetailPage";
import { StudioPage } from "./pages/StudioPage";
import { AuthProvider } from "./context/AuthContext";
import "./index.css";

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

const root = document.getElementById("root");
if (!root) {
  throw new Error("Missing #root");
}

createRoot(root).render(
  <StrictMode>
    <TonConnectUIProvider manifestUrl={manifestUrl}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<StudioPage />} />
              <Route path="runs" element={<DashboardPage />} />
              <Route path="gallery" element={<GalleryPage />} />
              <Route path="runs/:id" element={<RunDetailPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TonConnectUIProvider>
  </StrictMode>,
);
