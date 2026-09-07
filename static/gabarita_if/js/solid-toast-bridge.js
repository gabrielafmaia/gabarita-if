import { createComponent, render } from "https://esm.sh/solid-js@1.9.9/web?deps=solid-js@1.9.9";
import toast, { Toaster } from "https://esm.sh/solid-toast@0.5.0?deps=solid-js@1.9.9";

const toastOptions = {
  position: "top-right",
  gutter: 8,
  containerStyle: {
    "z-index": 2000,
  },
  toastOptions: {
    duration: 4000,
    unmountDelay: 300,
  },
};

const toastRoot = document.getElementById("solid-toast-root");

if (toastRoot) {
  render(() => createComponent(Toaster, toastOptions), toastRoot);
}

const showMessage = (messageElement) => {
  const message = messageElement.dataset.message;
  if (!message) {
    messageElement.remove();
    return;
  }

  switch (messageElement.dataset.messageLevel) {
    case "success":
      toast.success(message);
      break;
    case "error":
      toast.error(message);
      break;
    default:
      toast(message);
  }

  messageElement.remove();
};

const showDjangoMessages = (container = document) => {
  container.querySelectorAll(".django-message").forEach(showMessage);
};

window.gabaritaToast = {
  success: (message) => toast.success(message),
  error: (message) => toast.error(message),
  info: (message) => toast(message),
};

showDjangoMessages();

document.body.addEventListener("htmx:afterSwap", (event) => {
  showDjangoMessages();
});