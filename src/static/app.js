document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      console.log('Fetched activities:', activities);

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
          console.log('Participants for', name, details.participants);
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Participants:</h5>
            <ul class="participants-list" style="list-style-type:none; padding-left:0;"></ul>
          </div>
        `;

        // Add participants with delete icon
        const participantsUl = activityCard.querySelector('.participants-list');
        if (details.participants.length === 0) {
          const li = document.createElement('li');
          li.textContent = 'No participants yet.';
          li.style.color = '#888';
          participantsUl.appendChild(li);
        } else {
          details.participants.forEach((participant, idx) => {
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.alignItems = 'center';
            li.style.justifyContent = 'space-between';

            const nameSpan = document.createElement('span');
            nameSpan.textContent = participant;
            li.appendChild(nameSpan);

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '&#128465;'; // Trash can icon
            deleteBtn.title = 'Unregister';
            deleteBtn.onclick = async function() {
              await unregisterParticipant(name, participant);
            };
            li.appendChild(deleteBtn);

            participantsUl.appendChild(li);
          });
        }

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Unregister participant function
  async function unregisterParticipant(activityName, participantEmail) {
    try {
      const response = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(participantEmail)}`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchActivities();
      } else {
        const result = await response.json();
        alert(result.detail || 'Failed to unregister participant.');
      }
    } catch (error) {
      alert('Error unregistering participant.');
      console.error(error);
    }
  }

  // Initialize app
  fetchActivities();
});
