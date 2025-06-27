import React, { useEffect, useState } from "react";

export default function LiveConsole({ taskId, onDone }) {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:5173/ws/${taskId}`);
    ws.onmessage = evt => {
      const msg = JSON.parse(evt.data);
      setLines(l => [...l, JSON.stringify(msg)]);
      if (msg.state === "SUCCESS" || msg.state === "FAILURE") {
        onDone();
        ws.close();
      }
    };
    return () => ws.close();
  }, [taskId]);

  return (
    <pre
      style={{
        background: "#000",
        color: "#0f0",
        height: 200,
        overflowY: "scroll",
        padding: 10,
        fontSize: 12
      }}
    >
      {lines.join("\n")}
    </pre>
  );
}
