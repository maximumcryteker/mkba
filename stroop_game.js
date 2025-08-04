let results = [];
let questions = [];

fetch("config/questions.json")
  .then(res => res.json())
  .then(data => {
    questions = data;
    renderQuestions();
  })
  .catch(err => {
    console.error("Error loading or parsing questions:", err);
    const container = document.getElementById("questionnaire");
    if (container) {
      container.innerHTML = "<p style='color:red;'>Fehler beim Laden des Fragebogens.</p>";
    }
  });

function renderQuestions() {
  const container = document.getElementById("questionnaire");
  container.innerHTML = "";

  questions.forEach((q, i) => {
    const qDiv = document.createElement("div");
    qDiv.innerHTML = `<p>${q.question}</p>`;

    if (q.type === "radio" && q.options) {
      q.options.forEach((opt, j) => {
        const input = `<label><input type="radio" name="q${i}" value="${opt}">${opt}</label>`;
        qDiv.innerHTML += input;
      });
    } else if (q.type === "number") {
      qDiv.innerHTML += `<input type="number" name="q${i}" min="${q.min || ''}" max="${q.max || ''}">`;
    } else if (q.type === "text") {
      qDiv.innerHTML += `<input type="text" name="q${i}">`;
    } else if (q.scale) {
      q.scale.forEach((label, j) => {
        const input = `<label><input type="radio" name="q${i}" value="${j}">${label}</label>`;
        qDiv.innerHTML += input;
      });
    }

    container.appendChild(qDiv);
  });
}

document.getElementById("start-game").addEventListener("click", () => {
  const answers = {};
  questions.forEach((q, i) => {
    const val = document.querySelector(`input[name="q${i}"]:checked`);
    answers[`q${i}`] = val ? parseInt(val.value) : null;
  });

  document.getElementById("questionnaire").classList.add("hidden");
  document.getElementById("start-game").classList.add("hidden");
  startGame(answers);
});

function startGame(metadata) {
  const game = document.getElementById("game");
  game.classList.remove("hidden");

  const stimulus = document.getElementById("stimulus");
  const left = document.getElementById("left-touch");
  const right = document.getElementById("right-touch");

  const shapes = ["circle", "square", "triangle"];
  const colors = ["white", "red", "orange", "green"];
  const startTime = Date.now();
  const endTime = startTime + 60000;

  let timeout;
  function nextTrial() {
    const now = Date.now();
    if (now >= endTime) return endGame();

    const shape = shapes[Math.floor(Math.random() * shapes.length)];
    const color = colors[Math.floor(Math.random() * colors.length)];

    stimulus.style.backgroundColor = color;
    stimulus.style.borderRadius = shape === "circle" ? "50%" : "0";
    stimulus.style.clipPath = shape === "triangle" ? "polygon(50% 0%, 0% 100%, 100% 100%)" : "none";

    const correctKey = (color === "white" || color === "red") ? "1" : "2";
    const shownAt = Date.now();

    function handleResponse(key) {
      const time = Date.now() - shownAt;
      const correct = key === correctKey;
      results.push({ shape, color, key, time, correct });
      cleanup();
      nextTrial();
    }

    function onKey(e) {
      if (e.key === "1" || e.key === "2") handleResponse(e.key);
    }

    function onTouch(e) {
      const x = e.touches[0].clientX;
      const half = window.innerWidth / 2;
      handleResponse(x < half ? "1" : "2");
    }

    function cleanup() {
      document.removeEventListener("keydown", onKey);
      left.removeEventListener("touchstart", onTouch);
      right.removeEventListener("touchstart", onTouch);
    }

    document.addEventListener("keydown", onKey);
    left.addEventListener("touchstart", onTouch);
    right.addEventListener("touchstart", onTouch);
  }

  nextTrial();
}

function endGame() {
  document.getElementById("game").classList.add("hidden");
  document.getElementById("result-graph").classList.remove("hidden");

  const times = results.map(r => r.time);
  const correct = results.map(r => r.correct ? 1 : 0);

  const ctx = document.getElementById("result-graph").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: times.map((_, i) => i + 1),
      datasets: [
        {
          label: "Reaktionszeit (ms)",
          data: times,
          borderColor: "blue",
          yAxisID: 'y',
        },
        {
          label: "Richtigkeit",
          data: correct,
          borderColor: "green",
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      scales: {
        y: {
          type: 'linear',
          position: 'left',
        },
        y1: {
          type: 'linear',
          position: 'right',
          min: 0,
          max: 1,
          ticks: { stepSize: 1 }
        }
      }
    }
  });

  const data = Object.assign({}, results[0], {
    answers: JSON.stringify(results),
    timestamp: new Date().toISOString()
  });

  fetch("/upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}
