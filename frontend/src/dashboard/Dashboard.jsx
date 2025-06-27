import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard({ pid }) {
  const [chapters, setCh] = useState([]);
  const [themes, setThemes] = useState(null);
  const [cost, setCost] = useState(null);

  const load = () => {
    axios.get(`/projects/${pid}/chapters`).then(r => setCh(r.data));
    axios.get(`/projects/${pid}/costs`).then(r => setCost(r.data));
  };
  useEffect(load, [pid]);

  const regen = n =>
    axios
      .post(`/projects/${pid}/chapters/${n}/regenerate`)
      .then(r => pollTask(r.data.task_id));

  const pollTask = taskId => {
    const int = setInterval(() => {
      axios.get(`/tasks/${taskId}`).then(r => {
        if (r.data.ready) {
          clearInterval(int);
          load();
        }
      });
    }, 1500);
  };

  const fetchThemes = () =>
    axios.get(`/projects/${pid}/themes`).then(r => setThemes(r.data));

  return (
    <div style={{ marginTop: 20 }}>
      <h3>
        Cost so far: {cost ? `$${cost.usd}` : "—"} ({cost ? cost.tokens : "—"} tokens)
      </h3>
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
              <td style={{ color: ch.report && ch.report.missing.length ? "red" : "inherit" }}>
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
        Themes <button onClick={fetchThemes}>Refresh</button>
      </h2>
      {themes && (
        <table border="1" cellPadding="6">
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
    </div>
  );
}
