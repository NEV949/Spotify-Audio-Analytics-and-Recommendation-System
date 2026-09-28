import React from "react";
export default function ErrorState({ error }) {
  return (
    <div className="state error">
      <strong>Something went wrong.</strong>
      <span>{error?.message || "Unable to load data."}</span>
    </div>
  );
}
