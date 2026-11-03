"use strict";
document.getElementById("cors-fetch").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  const output = document.getElementById("cors-output");
  button.disabled = true;
  try {
    const response = await fetch(button.dataset.apiUrl, {credentials: "include"});
    output.textContent = `HTTP ${response.status}\n${await response.text()}`;
  } catch (error) {
    output.textContent = "Browser tidak dapat membaca respons. Pada mode diperbaiki, CORS menolak origin dashboard. Jika API belum aktif, periksa juga koneksi pada DevTools Network.";
  } finally { button.disabled = false; }
});
