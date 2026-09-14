(() => {
  const dialog = document.querySelector('#work-dialog');
  const form = document.querySelector('#work-form');
  const deleteDialog = document.querySelector('#delete-dialog');
  const deleteForm = document.querySelector('#delete-form');
  const createUrl = form.action;
  let deleteUrl;
  let returnFocus;
  const fieldNames = ['company_name', 'workplace', 'work_date', 'industry', 'amount', 'notes'];
  const amountInput = form.elements.amount;

  function formatAmount() {
    const raw = amountInput.value.replace(/,/g, '');
    if (!/^[0-9]*$/.test(raw)) return;
    const digitsBeforeCursor = amountInput.value.slice(0, amountInput.selectionStart).replace(/,/g, '').length;
    // Format strings directly to preserve large integer amounts without rounding.
    amountInput.value = raw.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    let cursor = 0;
    let digits = 0;
    while (cursor < amountInput.value.length && digits < digitsBeforeCursor) {
      if (amountInput.value[cursor] !== ',') digits++;
      cursor++;
    }
    amountInput.setSelectionRange(cursor, cursor);
  }
  amountInput.addEventListener('input', formatAmount);

  function clearErrors() {
    document.querySelector('#form-error').textContent = '';
    for (const name of fieldNames) {
      document.querySelector(`#error-${name}`).textContent = '';
      form.elements[name].removeAttribute('aria-invalid');
      form.elements[name].setAttribute('aria-describedby', `error-${name}`);
    }
  }
  function openForm(record = null) {
    form.reset();
    clearErrors();
    form.action = record ? record.dataset.editUrl : createUrl;
    form.elements.work_date.value = record ? record.dataset.date : form.dataset.date;
    if (record) {
      for (const [name, selector] of Object.entries({company_name: '.record-company', workplace: '.record-workplace', industry: '.record-industry', amount: '.record-amount', notes: '.record-notes'})) {
        form.elements[name].value = record.querySelector(selector).textContent;
      }
    }
    formatAmount();
    document.querySelector('#work-dialog-title').textContent = record ? '근무 내역 수정' : '근무 내역 추가';
    dialog.querySelector('.form-hint').textContent = record ? '입금 상태는 기존 상태로 유지됩니다. 비고는 선택 사항입니다.' : '새 내역은 미입금 상태로 저장됩니다. 비고는 선택 사항입니다.';
    returnFocus = document.activeElement;
    dialog.showModal();
    form.elements.company_name.focus();
  }
  function busy(target, value) {
    target.dataset.busy = String(value);
    target.querySelectorAll('button').forEach(button => { button.disabled = value; });
  }
  async function post(url, data) {
    const response = await fetch(url, {
      method: 'POST', body: data,
      headers: {'X-CSRFToken': form.elements.csrfmiddlewaretoken.value},
      credentials: 'same-origin'
    });
    let result;
    try { result = await response.json(); }
    catch { throw new Error('요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.'); }
    if (!response.ok) {
      const error = new Error(result.error || '입력 내용을 확인해 주세요.');
      error.fields = result.errors;
      throw error;
    }
    return result;
  }
  function navigate(date = form.dataset.date) {
    window.location.assign(`${form.dataset.calendarUrl}?${new URLSearchParams({date})}`);
  }
  for (const modal of [dialog, deleteDialog]) {
    modal.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => modal.close()));
    modal.addEventListener('cancel', event => {
      if (modal.querySelector('form').dataset.busy === 'true') event.preventDefault();
    });
    modal.addEventListener('close', () => returnFocus?.focus());
  }
  document.querySelector('#add-record').addEventListener('click', () => openForm());
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (form.dataset.busy === 'true') return;
    clearErrors();
    const data = new FormData(form);
    data.set('amount', amountInput.value.replace(/,/g, ''));
    busy(form, true);
    try {
      const result = await post(form.action, data);
      dialog.close();
      navigate(result.work_date);
    } catch (error) {
      document.querySelector('#form-error').textContent = error.message;
      for (const [name, errors] of Object.entries(error.fields || {})) {
        const output = document.getElementById(`error-${name}`);
        if (output) {
          output.textContent = errors.map(item => item.message).join(' ');
          form.elements[name].setAttribute('aria-invalid', 'true');
        }
      }
      document.querySelector('#form-error').focus();
    } finally { busy(form, false); }
  });
  document.querySelectorAll('.work-record').forEach(record => {
    record.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', async () => {
      if (button.dataset.action === 'edit') return openForm(record);
      if (button.dataset.action === 'delete') {
        returnFocus = button;
        deleteUrl = record.dataset.deleteUrl;
        document.querySelector('#delete-summary').textContent = `${record.querySelector('.record-company').textContent} · ${record.dataset.date} · ${record.querySelector('.record-amount').textContent}원`;
        document.querySelector('#delete-error').textContent = '';
        deleteDialog.showModal();
        return;
      }
      busy(record, true);
      document.querySelector('#page-error').textContent = '';
      try {
        await post(record.dataset.statusUrl, new URLSearchParams({status: button.dataset.status}));
        navigate();
      } catch (error) { document.querySelector('#page-error').textContent = error.message; }
      finally { busy(record, false); }
    }));
  });
  deleteForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (deleteForm.dataset.busy === 'true') return;
    busy(deleteForm, true);
    try {
      await post(deleteUrl, new FormData());
      deleteDialog.close();
      navigate();
    } catch (error) { document.querySelector('#delete-error').textContent = error.message; }
    finally { busy(deleteForm, false); }
  });
  if (dialog.dataset.open === 'true') {
    returnFocus = document.querySelector('#add-record');
    openForm();
    returnFocus = document.querySelector('#add-record');
    const url = new URL(window.location.href);
    url.searchParams.delete('new');
    window.history.replaceState(null, '', url);
  }
})();
