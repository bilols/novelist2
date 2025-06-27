import React, { useEffect, useState } from "react";
import axios from "axios";

const Selector = ({ list, value, onSel }) => (
  <select value={value} onChange={e => onSel(e.target.value)}>
    <option value="">-- choose project --</option>
    {list.map(p => (
      <option key={p.id} value={p.id}>
        {p.title}
      </option>
    ))}
  </select>
);

export default function App() {
  const [projects, setProjects] = useState([]);
  const [pid, setPid] = useState("");
  const [chapters, setCh] = useState([]);
  const [themes, setThemes] = useState(null);

  useEffect(() => {
    axios.get("/projects").then(r => setProjects(r.data));
  }, []);

  useEffect(() => {
    if (!pid) return;
    axios.get(`/projects/${pid}/chapters`).then(r => setCh(r.data));
    setThemes(null);
  }, [pid]);

  const regen = num =>
    axios
      .post(`/projects/${pid}/chapters/${num}/regenerate`)
      .then(() => alert(`Regeneration launched for chapter ${num}`));

  const fetchThemes = () =>
    axios
      .get(`/projects/${pid}/themes`)
      .then(r => setThemes(r.data))
      .catch(() => alert("Theme totals not found (add 'themes' to outline.json)"));

  return (
    <main style={{ fontFamily: "sans-serif", padding: 20 }}>
      <h1>Novelist 2.0 – Validation Dashboard</h1>
      <Selector list={projects} value={pid} onSel={setPid} />

      {chapters.length > 0 && (
        <>
          <h2>Chapters</h2>
          <table border="1" cellPadding="6">
            <thead>
              <tr>
                <th>#</th>
                <th>Status</th>
                <th>Missing beats</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {chapters.map(ch => (
                <tr key={ch.num}>
                  <td>{ch.num}</td>
                  <td>{ch.exists ? "✓" : "—"}</td>
                  <td style={{ color: "red" }}>
                    {ch.report && ch.report.missing.length
                      ? ch.report.missing.join("; ")
                      : ""}
                  </td>
                  <td>
                    <button onClick={() => regen(ch.num)}>Regenerate</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2 style={{ marginTop: 20 }}>
            Themes&nbsp;
            <button onClick={fetchThemes}>Refresh</button>
          </h2>
          {themes && (
            <table border="1" cellPadding="6">
              <thead>
                <tr>
                  <th>Theme</th>
                  <th>Hit Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(themes).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k}</td>
                    <td>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </main>
  );
}
