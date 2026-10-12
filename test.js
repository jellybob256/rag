import http from "k6/http";
import { sleep } from "k6";

export default function () {
  http.post(
    "http://localhost:8000/ask",
    JSON.stringify({ question: "What is Python?" }),
    { headers: { "Content-Type": "application/json" } }
  );
  sleep(1);
}