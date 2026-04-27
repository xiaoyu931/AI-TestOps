import { useState } from "react";
import { testopsApi } from "../api/testops";
import ExecutionTraceGraph from "../components/ExecutionTraceGraph";

export default function ExecutionTracePage() {
  const [cfgId, setCfgId] = useState("");
  const [data, setData] = useState<any[]>([]);

  const load = async () => {
    const exe = await testopsApi.getExecutions(Number(cfgId));

    const result = await Promise.all(
      exe.data.data.map(async (e: any) => {
        const comp = await testopsApi.getComponents(e.test_case_exe_id);
        return {
          execution: e.test_case_exe_id,
          components: comp.data.data.map((c: any) => ({
            name: c.component_name
          }))
        };
      })
    );

    setData(result);
  };

  return (
    <div>
      <h2>执行链路</h2>

      <input onChange={(e) => setCfgId(e.target.value)} />
      <button onClick={load}>查询</button>

      <ExecutionTraceGraph executions={data} />
    </div>
  );
}