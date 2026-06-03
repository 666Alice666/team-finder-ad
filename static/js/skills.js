(() => {
  const requestDelay = 220;
  const csrfToken = () => (window.getCookie ? window.getCookie("csrftoken") : "");

  function debounce(callback, delay) {
    let timerId = null;
    return (...args) => {
      clearTimeout(timerId);
      timerId = setTimeout(() => callback(...args), delay);
    };
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  }

  function postSkill(url, payload) {
    return requestJson(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
      },
      body: JSON.stringify(payload),
    });
  }

  function createSuggestion(text, dataset, className) {
    const item = document.createElement("li");
    item.textContent = text;
    item.className = className;
    Object.assign(item.dataset, dataset);
    return item;
  }

  function createChip(skill) {
    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.dataset.id = skill.id;
    chip.append(document.createTextNode(skill.name));

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-skill-btn";
    removeButton.title = "Удалить";
    removeButton.ariaLabel = "Удалить";
    removeButton.textContent = "×";
    chip.append(" ", removeButton);
    return chip;
  }

  function initProjectSkills() {
    const container = document.getElementById("skills-container");
    const addButton = document.getElementById("add-skill-btn");
    const inputBox = document.getElementById("skill-input-wrapper");
    const input = document.getElementById("skill-input");
    const list = document.getElementById("skill-suggestions");

    if (!container || !addButton || !inputBox || !input || !list) return;

    const projectId = container.dataset.projectId;
    const endpoints = {
      search: (query) => `/projects/skills/?q=${encodeURIComponent(query)}`,
      add: `/projects/${projectId}/skills/add/`,
      remove: (skillId) => `/projects/${projectId}/skills/${skillId}/remove/`,
    };

    const closeEditor = () => {
      inputBox.classList.add("hidden");
      list.classList.add("hidden");
      addButton.classList.remove("hidden");
    };

    const renderSuggestions = (items, query) => {
      list.replaceChildren();
      items.forEach((skill) => {
        list.append(createSuggestion(skill.name, { id: skill.id }, "suggestion-item"));
      });

      const exactMatch = items.some((skill) => skill.name.toLowerCase() === query.toLowerCase());
      if (!exactMatch) {
        list.append(createSuggestion(`Создать «${query}»`, { name: query }, "create-new"));
      }
      list.classList.toggle("hidden", !query);
    };

    const searchSkills = debounce(async () => {
      const query = input.value.trim();
      if (!query) {
        list.replaceChildren();
        list.classList.add("hidden");
        return;
      }
      renderSuggestions(await requestJson(endpoints.search(query)), query);
    }, requestDelay);

    const insertSkill = (skill) => {
      if (container.querySelector(`.skill-chip[data-id="${skill.id}"]`)) return;
      container.querySelector(".skill-empty")?.remove();
      container.insertBefore(createChip(skill), addButton);
    };

    const addSkill = async (payload) => {
      const skill = await postSkill(endpoints.add, payload);
      insertSkill(skill);
      closeEditor();
    };

    addButton.addEventListener("click", () => {
      addButton.classList.add("hidden");
      inputBox.classList.remove("hidden");
      input.value = "";
      list.replaceChildren();
      input.focus();
    });

    input.addEventListener("input", searchSkills);
    input.addEventListener("blur", () => setTimeout(closeEditor, 150));
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeEditor();
      }
      if (event.key === "Enter") {
        event.preventDefault();
        const firstItem = list.querySelector("li");
        const query = input.value.trim();
        if (firstItem?.dataset.id) {
          addSkill({ skill_id: firstItem.dataset.id });
        } else if (query) {
          addSkill({ name: query });
        }
      }
    });

    list.addEventListener("mousedown", (event) => {
      const item = event.target.closest("li");
      if (!item) return;
      addSkill(item.dataset.id ? { skill_id: item.dataset.id } : { name: item.dataset.name });
    });

    container.addEventListener("click", async (event) => {
      if (!event.target.classList.contains("remove-skill-btn")) return;
      const chip = event.target.closest(".skill-chip");
      await fetch(endpoints.remove(chip.dataset.id), {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken() },
      });
      chip.remove();
    });
  }

  document.addEventListener("DOMContentLoaded", initProjectSkills);
})();
