(() => {
  const csrfToken = () => (window.getCookie ? window.getCookie("csrftoken") : "");
  const notify = (message, type = "info") => {
    if (window.toast) {
      window.toast(message, { type });
      return;
    }
    alert(message);
  };

  async function postJson(url) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
      },
      body: "{}",
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }

  function setProjectClosed(button) {
    document.querySelector(".project-status-black").textContent = "Закрыт";
    button.remove();
    notify("Проект завершён");
  }

  function readParticipant(button) {
    return {
      id: button.dataset.userId,
      projectId: button.dataset.project,
      name: button.dataset.userName,
      avatar: button.dataset.userAvatar,
    };
  }

  function renderParticipant(member) {
    const link = document.createElement("a");
    link.href = `/users/${member.id}/`;
    link.id = `participant-${member.id}`;
    link.innerHTML = [
      '<div class="participant-item">',
      `<img src="${member.avatar}" alt="Аватар" class="participant-avatar">`,
      '<div class="participant-info">',
      `<span class="participant-name">${member.name}</span>`,
      '<span class="participant-role">Участник</span>',
      "</div>",
      "</div>",
    ].join("");
    return link;
  }

  function changeCounter(delta) {
    const counter = document.getElementById("participants-count");
    const nextValue = Number(counter.textContent) + delta;
    counter.textContent = String(nextValue);
    return nextValue;
  }

  function showEmptyParticipants() {
    const message = document.createElement("p");
    message.id = "no-participants";
    message.textContent = "Пока нет участников";
    document.getElementById("participants-list").appendChild(message);
  }

  function syncParticipantState(button, joined) {
    const member = readParticipant(button);
    const list = document.getElementById("participants-list");
    const currentRow = document.getElementById(`participant-${member.id}`);

    button.textContent = joined ? "Отказаться от участия" : "Участвовать";
    if (joined && !currentRow) {
      document.getElementById("no-participants")?.remove();
      list.appendChild(renderParticipant(member));
      changeCounter(1);
    }
    if (!joined && currentRow) {
      currentRow.remove();
      if (changeCounter(-1) === 0) {
        showEmptyParticipants();
      }
    }
  }

  function bindCompleteButton() {
    const button = document.getElementById("complete-project-btn");
    if (!button) return;

    button.addEventListener("click", async (event) => {
      event.preventDefault();
      try {
        const data = await postJson(`/projects/${button.dataset.id}/complete/`);
        data.status === "ok" ? setProjectClosed(button) : notify("Не удалось завершить проект", "error");
      } catch (error) {
        console.error(error);
        notify("Сервер не ответил. Попробуйте ещё раз.", "error");
      }
    });
  }

  function bindParticipationButton() {
    const button = document.getElementById("participate-btn");
    if (!button) return;

    button.addEventListener("click", async (event) => {
      event.preventDefault();
      try {
        const data = await postJson(`/projects/${button.dataset.project}/toggle-participate/`);
        if (data.status !== "ok") {
          notify("Не удалось изменить участие", "error");
          return;
        }
        syncParticipantState(button, data.participant);
      } catch (error) {
        console.error(error);
        notify("Сервер не ответил. Попробуйте ещё раз.", "error");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindCompleteButton();
    bindParticipationButton();
  });
})();
