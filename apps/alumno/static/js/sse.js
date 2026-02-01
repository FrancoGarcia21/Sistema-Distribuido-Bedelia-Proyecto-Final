export function startSSE(onEvent) {
  const ev = new EventSource("/events");
  ev.onmessage = (e) => {
    try { onEvent(JSON.parse(e.data)); }
    catch { onEvent({ type:"raw", data:e.data }); }
  };
  ev.onerror = () => onEvent({ type:"sse", event:"error" });
  return ev;
}
