"use strict";

const jq = $.noConflict();

jq(function ($) {
  const $entrysetForm = $("#entryset-form");
  const formsetPrefix = "entries";

  const ENTRY_FORM_SELECTOR = ".entry-form"

  $.fn.attachRemoveEntryFormListener = function () {
    this.click(function () {
      const entryId = this.dataset.entryId;
      const $entryElem = $entrysetForm
        .find(ENTRY_FORM_SELECTOR)
        .filter(function () {
          return this.dataset.entryId === entryId;
        });

      $entryElem.hide();
      $entryElem
        .find(`#id_${formsetPrefix}-${entryId}-DELETE`)
        .val("on");
    });

    return this;
  }

  const REMOVE_BUTTON_SELECTOR = ".remove-entry";

  $entrysetForm
    .find(REMOVE_BUTTON_SELECTOR)
    .attachRemoveEntryFormListener();

  const $totalFormsField = $(`#id_${formsetPrefix}-TOTAL_FORMS`, $entrysetForm);
  const $maxNumFormsField = $(`id_${formsetPrefix}-MAX_NUM_FORMS`, $entrysetForm);
  const $cloneForm = $("#empty-form");

  $.fn.attachAddEntryFormListener = function () {
    this.click(function () {
      const extraFormIndex = parseInt($totalFormsField.val(), 10);
      const maxNumForms = parseInt($maxNumFormsField.val(), 10);
      if (extraFormIndex >= maxNumForms) return;

      let extraFormHtml = $cloneForm
        .html()
        .replace(/__prefix__/g, extraFormIndex);
      extraFormHtml = $.parseHTML(extraFormHtml.trim());
      const $extraForm = $(extraFormHtml);
      $extraForm
        .find(REMOVE_BUTTON_SELECTOR)
        .attachRemoveEntryFormListener();
      $entrysetForm
        .find(ENTRY_FORM_SELECTOR)
        .last()
        .after($extraForm);

      $totalFormsField.val(extraFormIndex + 1);
    });

    return this;
  }

  const ADD_BUTTON_SELECTOR = "#add-entry";

  $entrysetForm
    .find(ADD_BUTTON_SELECTOR)
    .attachAddEntryFormListener();
});
