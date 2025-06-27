import React, { useState } from "react";
import axios from "axios";

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
  const [taskId, setTask] = useState(null);

  const next = () => setStep(s => s + 1);
  const prev = () => setStep(s => s - 1);

  const submit = () => {
    const payload = {
      ...form,
      themes: form.themes.split(",").map(s => s.trim()).filter(Boolean)
    };
    axios.post("/wizard", payload).then(r => {
      setTask(r.data.task_id);
      next();
    });
  };

  return (
    <div style={{ border: "1px solid gray", padding: 20, marginTop: 20 }}>
      {step === 1 && (
        <>
          <h3>Step 1 – Basic info</h3>
          <input
            placeholder="Title"
            value={form.title}
            onChange={e => setForm({ ...form, title: e.target.value })}
          />
          <input
            placeholder="Author"
            value={form.author}
            onChange={e => setForm({ ...form, author: e.target.value })}
          />
          <textarea
            placeholder="Premise"
            value={form.premise}
            onChange={e => setForm({ ...form, premise: e.target.value })}
            rows={3}
          />
          <button onClick={next} disabled={!form.title || !form.premise}>
            Next
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <h3>Step 2 – Targets & Themes</h3>
          <input
            type="number"
            value={form.words}
            onChange={e => setForm({ ...form, words: e.target.value })}
          />{" "}
          total words
          <input
            placeholder="Genre"
            value={form.genre}
            onChange={e => setForm({ ...form, genre: e.target.value })}
          />
          <input
            placeholder="Themes (comma‑sep)"
            value={form.themes}
            onChange={e => setForm({ ...form, themes: e.target.value })}
          />
          <div>
            <button onClick={prev}>Back</button>
            <button onClick={submit}>Launch Outline</button>
          </div>
        </>
      )}

      {step === 3 && (
        <>
          <h3>Generating outline…</h3>
          <p>Task id: {taskId}</p>
        </>
      )}

      <button onClick={onClose}>Close</button>
    </div>
  );
}
