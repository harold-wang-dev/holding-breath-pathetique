async function readCsv(path) {
  const text = await fetch(path).then((response) => response.text());
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.map((line) => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] ?? "";
    });
    return row;
  });
}

async function loadAudioPaths() {
  try {
    return await fetch("audio_paths.json").then((response) => response.json());
  } catch (error) {
    return {};
  }
}

async function main() {
  const events = await readCsv("../data/events.csv");
  const audioPaths = await loadAudioPaths();
  const sourceEvents = events.filter((row) => row.condition === "source");
  const recordings = [...new Set(sourceEvents.map((row) => row.recording_id))];
  const recordingSelect = document.getElementById("recording");
  const pauseSelect = document.getElementById("pause");
  const output = document.getElementById("output");

  recordings.forEach((recordingId) => {
    const option = document.createElement("option");
    option.value = recordingId;
    option.textContent = recordingId;
    recordingSelect.appendChild(option);
  });

  document.getElementById("show").addEventListener("click", () => {
    const selected = sourceEvents.find(
      (row) => row.recording_id === recordingSelect.value && row.pause === pauseSelect.value
    );
    output.textContent = JSON.stringify(
      {
        event: selected ?? null,
        local_audio_path: audioPaths[recordingSelect.value] ?? "not configured"
      },
      null,
      2
    );
  });
}

main();
