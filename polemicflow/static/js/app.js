"use strict";

$(function ($) {
  $(".set .collapse-open").click(function (ev) {
    $(ev.currentTarget)
      .closest(".set")
      .find(".card .collapse")
      .collapse("show");
  });

  $(".set .collapse-close").click(function (ev) {
    $(ev.currentTarget)
      .closest(".set")
      .find(".card .collapse")
      .collapse("hide");
  });
});
