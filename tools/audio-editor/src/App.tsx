import { useEffect, useState } from "react";
import PickerPage from "./pages/PickerPage";
import EditorPage from "./pages/EditorPage";
import AppHeader from "./components/AppHeader";

type Route =
  | { name: "picker" }
  | { name: "editor"; slug: string };

function parseHash(hash: string): Route {
  const match = hash.match(/^#\/edit\/([^/?#]+)/);
  if (match) return { name: "editor", slug: decodeURIComponent(match[1]) };
  return { name: "picker" };
}

export default function App() {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash));

  useEffect(() => {
    const onHashChange = () => setRoute(parseHash(window.location.hash));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader inEditor={route.name === "editor"} />
      <main className="flex-1 flex flex-col">
        {route.name === "picker" ? (
          <PickerPage />
        ) : (
          <EditorPage key={route.slug} slug={route.slug} />
        )}
      </main>
    </div>
  );
}
