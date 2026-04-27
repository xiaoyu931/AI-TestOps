import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

export default function TemplateExplorer({ templateId }: any) {
  const [data, setData] = useState<any>();

  useEffect(() => {
    if (!templateId) return;
    testopsApi.getTemplateDetail(templateId).then((res: any) => {
      setData(res.data);
    });
  }, [templateId]);

  return (
    <div>
      <h3>模板结构</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}