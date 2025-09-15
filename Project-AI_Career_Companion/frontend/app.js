const API_BASE = "";

// --- Tab switching ---
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    tabButtons.forEach(b => b.classList.remove("active"));
    tabContents.forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// --- Skills Gap ---
document.getElementById("skillsForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    current_role: document.getElementById("skillsCurrentRole").value,
    target_role: document.getElementById("skillsTargetRole").value,
    skills: document.getElementById("skillsList").value.split(","),
    desired_skills: document.getElementById("desiredSkills").value.split(",")
  };
  callAPI("/analyze_skills", payload, "skillsResult");
});

// --- Career Plan ---
document.getElementById("planForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    current_role: document.getElementById("planCurrentRole").value,
    target_role: document.getElementById("planTargetRole").value,
    available_trainings: document.getElementById("planTrainings").value.split(",")
  };
  callAPI("/generate_plan", payload, "planResult");
});

// --- Performance Review ---
document.getElementById("reviewForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    employee_name: document.getElementById("reviewName").value,
    achievements: document.getElementById("reviewAchievements").value.split(","),
    challenges: document.getElementById("reviewChallenges").value.split(","),
    goals: document.getElementById("reviewGoals").value.split(",")
  };
  callAPI("/performance_review", payload, "reviewResult");
});

// --- Mentorship ---
document.getElementById("mentorForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    role: document.getElementById("mentorRole").value,
    scenario: document.getElementById("mentorScenario").value
  };
  callAPI("/mentor_simulation", payload, "mentorResult");
});

// --- Generic API Caller ---
async function callAPI(endpoint, payload, resultId) {
  try {
    const res = await fetch(API_BASE + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    const key = Object.keys(data)[0]; // pick first key ("analysis", "plan", etc.)
    document.getElementById(resultId).innerText = data[key] || "No response.";
  } catch (err) {
    document.getElementById(resultId).innerText = "Error: " + err.message;
  }
}
