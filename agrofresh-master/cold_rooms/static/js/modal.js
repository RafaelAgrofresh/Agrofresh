import { getUUID } from '/static/comms/js/jsobject.js';

export function confirmDialog(title, body, yesLabel, noLabel, handler) {
    const modalId = getUUID();

    $(`<div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">${body}</div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary btn-yes">${yesLabel}</button>
                        <button type="button" class="btn btn-secondary btn-no">${noLabel}</button>
                    </div>
                </div>
            </div>
        </div>`).appendTo('body');

    $(`#${modalId}`).modal({
        backdrop: 'static',
        keyboard: false,
    });

    $(`#${modalId} .btn-yes`).click(() => {
        $(`#${modalId}`).modal("hide");
        handler(true);
    });

    $(`#${modalId} .btn-no`).click(() => {
        $(`#${modalId}`).modal("hide");
        handler(false);
    });

    $(`#${modalId}`).on('hidden.bs.modal', () => {
        $(`#${modalId}`).remove();
    });
}

export function confirmDialogCustom(title, body, yesLabel, noLabel, customLabel, handler) {
    const modalId = getUUID();

    $(`<div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">${body}</div>
                    <div class="modal-footer">

                        <button type="button" class="btn btn-primary btn-yes">${yesLabel}</button>
                        <button type="button" class="btn btn-secondary btn-no">${noLabel}</button>
                        <button type="button" class="btn btn-dark btn-custom">${customLabel}</button>
                    </div>
                </div>
            </div>
        </div>`).appendTo('body');

    $(`#${modalId}`).modal({
        backdrop: 'static',
        keyboard: false,
    });

    $(`#${modalId} .btn-yes`).click(() => {
        $(`#${modalId}`).modal("hide");
        handler("yes");
    });

    $(`#${modalId} .btn-no`).click(() => {
        $(`#${modalId}`).modal("hide");
        handler("no");
    });

    $(`#${modalId} .btn-custom`).click(() => {
        $(`#${modalId}`).modal("hide");
        handler("custom");
    });

    $(`#${modalId}`).on('hidden.bs.modal', () => {
        $(`#${modalId}`).remove();
    });
}

export function notifyDialog(title, body, okLabel, handler) {
    const modalId = getUUID();

    $(`<div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">${body}</div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary btn-ok">${okLabel}</button>
                    </div>
                </div>
            </div>
        </div>`).appendTo('body');

    $(`#${modalId}`).modal({
        backdrop: 'static',
        keyboard: false,
    });

    $(`#${modalId} .btn-ok`).click(() => {
        $(`#${modalId}`).modal("hide");
        if (handler) handler();
    });

    $(`#${modalId}`).on('hidden.bs.modal', () => {
        $(`#${modalId}`).remove();
    });
}
