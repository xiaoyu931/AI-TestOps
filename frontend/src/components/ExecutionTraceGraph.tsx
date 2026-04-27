export default function ExecutionTraceGraph({ executions }: any) {
  return (
    <div>
      {executions.map((exe: any) => (
        <div key={exe.execution}>
          <h4>{exe.execution}</h4>
          {exe.components.map((c: any) => (
            <span key={c.name}> → {c.name}</span>
          ))}
        </div>
      ))}
    </div>
  );
}
