/**
 * Safe Edits
 * Author: Luc Belliveau
 * 
 * This library helps to prevent navigation away from a page when
 * form elements are modified.
 * 
 * Usage:
 * 
 * Register form elements to monitor for changes, then activate the
 * library.
 * 
 */
const safe_edits = {
  _frozen: false,
  _getValue: (element) => {
    if (element.hasAttribute("data-safe-edits-value")) {
      return element.getAttribute("data-safe-edits-value");
    }
    if (
      element.tagName.toUpperCase() === "INPUT" &&
      ["checkbox", "radio"].includes(element.type)
    ) {
      return element.checked;
    }
    return element.value;
  },
  isDirty: () => {
    const blockers = document.querySelectorAll("*[data-safe-edits-block=true]");
    const bypass = document.querySelectorAll("*[data-safe-edits-bypass=true]");
    const members = Array.from(
      document.querySelectorAll("*[data-safe-edits-member=true]")
    );
    return (
      bypass.length === 0 &&
      (blockers.length > 0 ||
        (safe_edits._frozen !== false &&
          (!safe_edits._frozen.every((m) => members.includes(m)) ||
            !members.every((m) => safe_edits._frozen.includes(m)))))
    );
  },
  triggerDirtyUpdate: () => {
    document.body.dispatchEvent(
      new CustomEvent("safe_edits:dirty", { detail: safe_edits.isDirty() })
    );
    return safe_edits;
  },
  isFrozen: () => {
    return safe_edits._frozen;
  },
  freeze: (frozen = true) => {
    safe_edits._frozen = frozen
      ? Array.from(document.querySelectorAll("*[data-safe-edits-member=true]"))
      : false;
    return safe_edits;
  },
  beforeUnloadListener: (event) => {
    if (safe_edits.isDirty()) {
      event.preventDefault();
      return (event.returnValue = "stop");
    }
  },
  setupInputListener: (element, event_type, original_value) => {
    element.setAttribute("data-safe-edits-member", true);
    safe_edits.triggerDirtyUpdate();
    element.addEventListener(event_type, function (event) {
      if (safe_edits._getValue(element) !== original_value) {
        event.target.setAttribute("data-safe-edits-block", true);
      } else {
        event.target.removeAttribute("data-safe-edits-block");
      }
      safe_edits.triggerDirtyUpdate();
    });
    return safe_edits;
  },
  setupBypassListener: (element, event_type) => {
    safe_edits.triggerDirtyUpdate();
    element.addEventListener(event_type, function (event) {
      event.target.setAttribute("data-safe-edits-bypass", "true");
      setTimeout(function () {
        event.target.removeAttribute("data-safe-edits-bypass");
      }, 500);
    });
    return safe_edits;
  },
  setupResetListener: (element, event_type = "click") => {
    safe_edits.triggerDirtyUpdate();
    const parent =
      element.closest("*[data-safe-edits-container=true]") || document.body;
    element.addEventListener(event_type, function (event) {
      const elements = parent.querySelectorAll("*[data-safe-edits-block=true]");
      for (const el of elements) {
        el.removeAttribute("data-safe-edits-block");
      }
      safe_edits.triggerDirtyUpdate();
    });
    return safe_edits;
  },
  setupListener: (element_id, tagName, event_type, listener) => {
    const element = document.getElementById(element_id);
    const children = Array.from(element.getElementsByTagName(tagName));
    if (element.tagName.toUpperCase() === tagName.toUpperCase()) {
      children.push(element);
    }
    for (const el of children) {
      listener(el, event_type, safe_edits._getValue(el));
    }
    return safe_edits;
  },
  register: (parentId, tagNames = "input,select", event_type = "input") => {
    for (const tagName of tagNames.split(",")) {
      safe_edits.setupListener(
        parentId,
        tagName,
        event_type,
        safe_edits.setupInputListener
      );
    }
    return safe_edits;
  },
  register_bypass: (parentId, tagNames = "input", event_type = "click") => {
    for (const tagName of tagNames.split(",")) {
      safe_edits.setupListener(
        parentId,
        tagName,
        event_type,
        safe_edits.setupBypassListener
      );
    }
    return safe_edits;
  },
  register_reset: (parentId, tagNames = "input", event_type = "click") => {
    for (const tagName of tagNames.split(",")) {
      safe_edits.setupListener(
        parentId,
        tagName,
        event_type,
        safe_edits.setupResetListener
      );
    }
    return safe_edits;
  },
  activate: () => {
    window.addEventListener(
      "beforeunload",
      safe_edits.beforeUnloadListener,
      true
    );
    return safe_edits;
  },
  deactivate: () => {
    window.removeEventListener(
      "beforeunload",
      safe_edits.beforeUnloadListener,
      true
    );
    return safe_edits;
  },
  bypass: (value = true) => {
    if (value) {
      document.body.setAttribute("data-safe-edits-bypass", value);
    } else {
      document.body.removeAttribute("data-safe-edits-bypass");
    }
    return safe_edits;
  },
};
