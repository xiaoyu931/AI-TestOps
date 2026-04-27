export function getCaseExecutionStateText(value: number) {
  switch (value) {
    case 1: return "Running"
    case 2: return "Success"
    case 3: return "Failed"
    case 4: return "Verifying"
    case 5: return "Verify Success"
    case 6: return "Verify Failed"
    case 7: return "Triggered Verify"
    case 8: return "UiPath Success"
    case 9: return "Order Processing"
    case 10: return "Order Success"
    case 11: return "Order Failed"
    case 12: return "Triggered Order"
    case 13: return "No Order Needed"
    case 14: return "No Verify Needed"
    default: return "-"
  }
}



export function getComponentExecutionStateText(value: number) {
  const map: Record<number, string> = {
    0: "Init",
    2: "Success",
    3: "Failed",
  };

  return map[value] || "-";
}

export function getComponentExecutionStateColor(value: number) {
  const map: Record<number, string> = {
    0: "#999",
    2: "#16a34a",
    3: "#dc2626",
  };

  return map[value] || "#666";
}