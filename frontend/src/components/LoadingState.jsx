import React from "react";
export default function LoadingState({ text = "Loading..." }) {
  return <div className="state">{text}</div>;
}
