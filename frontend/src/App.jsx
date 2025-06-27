import React, { useEffect, useState } from "react";
import axios from "axios";
import Wizard from "./wizard/Wizard";
import Dashboard from "./dashboard/Dashboard";

export default function App() {
  const [projects, setProjects] = useState([]);
  const [pid, setPid] = useState("");
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    axios.get("/projects").then(r => setProjects(r.data));
  }, [showWizard]);

  return (
    <main style={{ fontFamily: "sans-serif", padding: 20 }}>
      <h1>Novelist 2.0</h1>
      <button onClick={() => setShowWizard(true)}>Start New Novel</button>

      {!showWizard && (
        <>
          <h2>Your Projects</h2>
          <select value={pid} onChange={e => setPid(e.target.value)}>
            <option value="">-- choose project --</option>
            {projects.map(p => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
          {pid && <Dashboard pid={pid} />}
        </>
      )}

      {showWizard && <Wizard onClose={() => setShowWizard(false)} />}
    </main>
  );
}
