"use strict";

const feedback = document.getElementById("feedback");

function showError(error) {
  if (!feedback) return;
  feedback.textContent = error.message || "Something went wrong. Please try again.";
  feedback.hidden = false;
  feedback.scrollIntoView({ block: "nearest" });
}

async function apiRequest(endpoint, method, payload) {
  const options = { method, headers: { Accept: "application/json" } };
  if (payload !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(endpoint, options);
  if (response.status === 204) return null;
  const body = await response.json();
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail)
      ? detail.map(item => `${item.loc.filter(part => part !== "body").join(".") || "Request"}: ${item.msg}`).join("; ")
      : detail || "The request could not be completed.";
    throw new Error(message);
  }
  return body;
}

const taskForm = document.getElementById("task-form");
if (taskForm) {
  taskForm.addEventListener("submit", async event => {
    event.preventDefault();
    const title = taskForm.elements.title.value.trim();
    if (!title) {
      showError(new Error("Enter a title containing at least one non-space character."));
      taskForm.elements.title.focus();
      return;
    }
    const submit = taskForm.querySelector('button[type="submit"]');
    const originalText = submit.textContent;
    submit.disabled = true;
    submit.textContent = "Saving…";
    feedback.hidden = true;
    try {
      const task = await apiRequest(taskForm.dataset.endpoint, taskForm.dataset.method, {
        title,
        description: taskForm.elements.description.value || null,
        status: taskForm.elements.status.value
      });
      window.location.assign(`/ui/tasks/${task.id}`);
    } catch (error) {
      showError(error);
    } finally {
      submit.disabled = false;
      submit.textContent = originalText;
    }
  });
}

const deleteDialog = document.getElementById("delete-dialog");
if (deleteDialog) {
  document.getElementById("delete-open").addEventListener("click", () => deleteDialog.showModal());
  document.getElementById("delete-cancel").addEventListener("click", () => deleteDialog.close());
  const confirm = document.getElementById("delete-confirm");
  confirm.addEventListener("click", async () => {
    confirm.disabled = true;
    confirm.textContent = "Deleting…";
    feedback.hidden = true;
    try {
      await apiRequest(confirm.dataset.endpoint, "DELETE");
      window.location.assign("/ui/tasks");
    } catch (error) {
      deleteDialog.close();
      showError(error);
    } finally {
      confirm.disabled = false;
      confirm.textContent = "Delete task";
    }
  });
}
