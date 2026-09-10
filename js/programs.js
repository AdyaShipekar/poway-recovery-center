document.addEventListener("DOMContentLoaded", () => {
  const meetings = [
    {name:"Morning Grounding", day:"Monday", time:"9:00 AM", type:"Peer-led · In person", spots:8},
    {name:"Recovery Check-In", day:"Tuesday", time:"6:00 PM", type:"Peer-led · Hybrid", spots:12},
    {name:"Family & Supporters", day:"Wednesday", time:"7:00 PM", type:"Facilitated · Online", spots:10},
    {name:"Skills for Urges", day:"Thursday", time:"5:30 PM", type:"Workshop · In person", spots:6},
    {name:"Weekend Connection", day:"Saturday", time:"10:30 AM", type:"Peer-led · In person", spots:14}
  ];
  const schedule = document.querySelector("#schedule");
  const saved = JSON.parse(localStorage.getItem("prc-meetings") || "{}");
  function render() {
    schedule.innerHTML = "";
    meetings.forEach((m, i) => {
      const reserved = saved[i] || 0, remaining = Math.max(0, m.spots - reserved);
      const el = document.createElement("article"); el.className="meeting";
      el.innerHTML = `<div><div class="meeting-meta">${m.day} · ${m.time}</div><h3>${m.name}</h3><p>${m.type}</p></div><div><span class="spots">${remaining} spots available</span><button class="button button-primary" ${remaining===0?"disabled":""}>${remaining===0?"Full":"Reserve spot"}</button></div>`;
      el.querySelector("button").addEventListener("click", () => { saved[i]=(saved[i]||0)+1; localStorage.setItem("prc-meetings",JSON.stringify(saved)); render(); });
      schedule.appendChild(el);
    });
  }
  render();
});