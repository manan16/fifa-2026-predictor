import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Bracket from "./pages/Bracket";
import Fixtures from "./pages/Fixtures";
import Home from "./pages/Home";
import MatchPrediction from "./pages/MatchPrediction";
import ModelInfo from "./pages/ModelInfo";
import Teams from "./pages/Teams";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/bracket" element={<Bracket />} />
        <Route path="/fixtures" element={<Fixtures />} />
        <Route path="/fixtures/:fixtureId" element={<MatchPrediction />} />
        <Route path="/teams" element={<Teams />} />
        <Route path="/model" element={<ModelInfo />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
