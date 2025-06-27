import React, { useState } from "react";
import axios from "axios";
import LiveConsole from "../components/LiveConsole";

export default function Wizard({ onClose }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    title: "",
    author: "",
    premise: "",
    words: 60000,
    themes: "",
    genre: ""
  });
  const [taskId, setTaskId] = useState(null);

  const next = () => setStep(s => s + 1);
  const prev = () => setStep(s => s - 1);

  const launch = () => {
    const payload = {
      ...form,
      themes: form.themes.split(",").map(t => t.trim()).filter(Boolean)
    };
    axios.post("/wizard", payload).then(r => {
      setTaskId(r.data.task_id);
      next();
    });
  };

  const label = { display: "block", marginTop: 8 };

  return (
    <div style={{ border: "1px solid gray", padding: 20, marginTop: 20 }}>
      {step === 1 && (
        <>
          <h3>Step 1 – Basic Info</h3>
          <label style={label}>
            Title
            <input
              value={form.title}
              onChange={e => setForm({ ...form, title: e.target.value })}
            />
          </label>
          <label style={label}>
            Author
            <input
              value={form.author}
              onChange={e => setForm({ ...form, author: e.target.value })}
            />
          </label>
          <label style={label}>
            Premise
            <textarea
              rows={3}
              value={form.premise}
              onChange={e => setForm({ ...form, premise: e.target.value })}
            />
          </label>
          <button onClick={next} disabled={!form.title || !form.premise}>
            Next
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <h3>Step 2 – Targets & Themes</h3>
          <label style={label}>
            Total word count for novel
            <input
              type="number"
              value={form.words}
              onChange={e => setForm({ ...form, words: e.target.value })}
            />
          </label>
          <label style={label}>
            Genre
            <input
              value={form.genre}
              onChange={e => setForm({ ...form, genre: e.target.value })}
            />
          </label>
          <label style={label}>
            Themes (comma‑separated)
            <input
              value={form.themes}
              onChange={e => setForm({ ...form, themes: e.target.value })}
            />
          </label>
          <div style={{ marginTop: 10 }}>
            <button onClick={prev}>Back</button>{" "}
            <button onClick={launch}>Launch Outline</button>
          </div>
        </>
      )}

      {step === 3 && (
        <>
          <h3>Generating outline…</h3>
          <LiveConsole taskId={taskId} onDone={onClose} />
        </>
      )}

      <button onClick={onClose} style={{ marginTop: 15 }}>
        Close
      </button>
    </div>
  );
}
