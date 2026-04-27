import { useState, useEffect } from "react";

export default function JsonEditor({ label, value, onChange }: any) {
  const [text, setText] = useState("");

  useEffect(() => {
    setText(JSON.stringify(value || {}, null, 2));
  }, [value]);

  return (
    <div>
      <label>{label}</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={() => {
          try {
            onChange(JSON.parse(text));
          } catch {
            alert("JSON错误");
          }
        }}
      />
    </div>
  );
}