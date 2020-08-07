"use strict";

$(function ($) {
  const USER_DETAIL_TAB_KEY = "user_detail_tab";

  $(document).on("show.bs.tab", function (ev) {
    const tabId = ev.target.id;
    if (!tabId) {
      console.warn("Specify tab id(s).");
      return;
    }
    localStorage.setItem(USER_DETAIL_TAB_KEY, tabId);
  });

  const tabId = localStorage.getItem(USER_DETAIL_TAB_KEY);
  if (!tabId) return;
  const $tabElem = $("#" + tabId);
  if (!$tabElem.length) {
    console.warn(`Tab element with id "${tabId}" not found.`);
    return;
  }
  $tabElem.tab("show");
  // Remove the tab key value after reload show
  localStorage.removeItem(USER_DETAIL_TAB_KEY);
});
