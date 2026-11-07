'use strict';

const $ = (selector, root = document) => root.querySelector(selector);
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = {NEW:'New report',CLARIFYING:'Needs details',REPRODUCED:'Reproduced',PATCH_READY:'Patch ready',VERIFIED:'Awaiting review',APPROVED:'Approved',CLOSED:'Closed',NEEDS_HUMAN:'Needs attention'};
const state = {cases:[],selected:null,view:null,tab:'overview',page:'desk',busy:false,job:null,refreshing:false};
const hash = new URLSearchParams(location.hash.slice(1));
if (hash.has('token')) {
  sessionStorage.setItem('proofdesk-token', hash.get('token'));
  history.replaceState(null, '', location.pathname);
}
let token = sessionStorage.getItem('proofdesk-token') || '';
let toastTimer;

async function api(path, data) {
  const response = await fetch(path, {method:data === undefined ? 'GET' : 'POST',
    headers:{Authorization:`Bearer ${token}`, ...(data === undefined ? {} : {'Content-Type':'application/json'})},
    ...(data === undefined ? {} : {body:JSON.stringify(data)})});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `Request failed (${response.status})`);
  return result;
}

function alertError(error) {
  $('#alert').textContent = error.message || String(error);
  $('#alert').hidden = false;
}
function clearError() { $('#alert').hidden = true; }
function toast(message) {
  $('#toast').textContent = message;
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 3500);
}
function badge(status) {
  const tone = ['VERIFIED','APPROVED','CLOSED'].includes(status) ? 'positive' :
    ['CLARIFYING','NEEDS_HUMAN'].includes(status) ? 'pending' : '';
  return `<span class="badge ${tone}"><span aria-hidden="true">${tone === 'positive' ? '✓' : '·'}</span>${escapeHTML(labels[status] || status)}</span>`;
}
function date(value) { return new Date(value).toLocaleString([], {month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}); }
function relative(value) {
  const minutes = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60000));
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
  return new Date(value).toLocaleDateString([], {month:'short',day:'numeric'});
}
function showPage(page) {
  state.page = page;
  $('#desk-view').hidden = page !== 'desk';
  $('#detail-view').hidden = page !== 'detail';
  $('#setup-view').hidden = page !== 'setup';
  $('#nav-cases').classList.toggle('active', page !== 'setup');
  $('#nav-connection').classList.toggle('active', page === 'setup');
  $('#breadcrumb').textContent = page === 'setup' ? 'Switch setup' : page === 'detail' ? 'Case evidence' : 'Case desk';
}
function renderCases() {
  const cases = state.cases;
  $('#metric-total').textContent = cases.length;
  $('#metric-review').textContent = cases.filter(c => c.state === 'VERIFIED').length;
  $('#metric-progress').textContent = cases.filter(c => !['VERIFIED','APPROVED','CLOSED'].includes(c.state)).length;
  $('#metric-closed').textContent = cases.filter(c => c.state === 'CLOSED').length;
  $('#nav-count').textContent = cases.length;
  const query = $('#search').value.toLowerCase().trim();
  const filter = $('#filter').value;
  const visible = cases.filter(c => `${c.id} ${c.report.summary || ''}`.toLowerCase().includes(query))
    .filter(c => filter === 'all' || (filter === 'review' && c.state === 'VERIFIED') ||
      (filter === 'closed' && c.state === 'CLOSED') ||
      (filter === 'active' && !['VERIFIED','APPROVED','CLOSED'].includes(c.state)));
  $('#table-count').textContent = visible.length;
  if (!visible.length) {
    $('#case-list').innerHTML = `<div class="empty"><span class="empty-icon" aria-hidden="true">${cases.length ? '⌕' : '↗'}</span><h3>${cases.length ? 'No matching cases.' : 'Your first report starts here.'}</h3><p>${cases.length ? 'Try a different search or status filter.' : 'Open a case with a reproducible report, then bring your agents together in Switch. This desk fills with their actual work.'}</p>${cases.length ? '' : '<button class="secondary" id="empty-create">＋ Create your first case</button>'}</div>`;
    $('#empty-create')?.addEventListener('click', openNewCase);
    return;
  }
  $('#case-list').innerHTML = visible.map(c => `<button class="case-row" data-case="${escapeHTML(c.id)}"><span><span class="case-title">${escapeHTML(c.report.summary || 'Incomplete report')}</span><span class="case-id">${escapeHTML(c.id)}</span></span><span>${badge(c.state)}</span><span class="candidate-count">${c.total_attempts} ${c.total_attempts === 1 ? 'attempt' : 'attempts'}</span><span class="updated" title="${escapeHTML(date(c.updated_at))}">${escapeHTML(relative(c.updated_at))}</span><span class="row-arrow" aria-hidden="true">↗</span></button>`).join('');
  document.querySelectorAll('[data-case]').forEach(button => button.addEventListener('click', () => openCase(button.dataset.case)));
}

async function refresh({detail = false} = {}) {
  if (state.refreshing) return;
  state.refreshing = true;
  try {
    const result = await api('/api/cases');
    state.cases = result.cases;
    renderCases();
    $('#connection-text').textContent = 'Local workspace connected';
    $('#connection-dot').className = 'status-dot';
    if (result.errors.length) alertError(new Error(`${result.errors.length} case record(s) could not be read. Check the case store.`));
    if (detail && state.selected && state.page === 'detail' && !state.busy) {
      const selected = state.selected;
      const view = await api(`/api/cases/${selected}`);
      if (state.selected !== selected || state.page !== 'detail') return;
      if (!state.view || JSON.stringify(view.case) !== JSON.stringify(state.view.case)) {
        // Preserve a review in progress; the server rejects stale evidence on submission.
        if (!$('#detail-view form')?.contains(document.activeElement)) {
          state.view = view;
          renderDetail();
        }
      }
    }
  } catch (error) {
    $('#connection-text').textContent = 'Workspace unavailable';
    $('#connection-dot').className = 'status-dot error';
    alertError(error);
    if (!state.cases.length) $('#case-list').innerHTML = '<div class="empty"><h3>Unable to load the workspace.</h3><p>Start the local server and open its full terminal URL, including the private access token. Then refresh.</p></div>';
  } finally { state.refreshing = false; }
}

async function openCase(id) {
  clearError();
  state.selected = id;
  state.tab = 'overview';
  showPage('detail');
  $('#detail-view').innerHTML = '<p class="loading" role="status">Reading case evidence…</p>';
  try {
    const view = await api(`/api/cases/${id}`);
    if (state.selected !== id || state.page !== 'detail') return;
    state.view = view; renderDetail();
  }
  catch (error) { alertError(error); }
}

function evidenceFor(key) {
  const ref = key === 'response' ? state.view.case.response : state.view.case[key]?.evidence;
  return ref ? state.view.evidence.find(item => item.reference.path === ref.path) : null;
}
function checksHTML(item, title) {
  if (!item) return `<div class="panel"><h2>${title}</h2><p class="muted">No recorded checks yet. Results appear after an agent executes the workflow command.</p></div>`;
  if (!item.valid) return `<div class="panel"><h2>${title}</h2><p class="form-error">Evidence integrity failed: ${escapeHTML(item.error)}</p></div>`;
  const data = item.data;
  return `<div class="panel"><p class="eyebrow">${escapeHTML(data.policy)}</p><h2>${title}</h2><p class="small-note">Commit ${escapeHTML(data.commit)} · ${data.duration_seconds}s · exit ${data.exit_code}</p>${data.infrastructure_error ? `<p class="form-error">${escapeHTML(data.infrastructure_error)}</p>` : ''}<table class="evidence-table"><thead><tr><th>CHECK</th><th>EXPECTED</th><th>ACTUAL</th><th>RESULT</th></tr></thead><tbody>${data.checks.map(check => `<tr><td>${escapeHTML(check.id)}</td><td>${escapeHTML(check.expected || '—')}</td><td>${escapeHTML(check.actual ?? check.error ?? (check.passed ? 'ValueError' : '—'))}</td><td class="${check.passed ? 'check-pass' : 'check-fail'}">${check.passed ? 'PASS' : 'FAIL'}</td></tr>`).join('')}</tbody></table><p class="integrity">✓ Evidence hash matches the stored reference</p></div>`;
}

function overviewHTML(c) {
  const response = evidenceFor('response');
  const contexts = state.view.evidence.filter(item => item.valid && item.reference.path.startsWith('evidence/switch-context-'));
  const contextPanel = contexts.length ? `<article class="panel"><p class="eyebrow">SWITCH CONVERSATION</p><h2>Where the work happened</h2>${contexts.map(item => `<dl><dt>Room</dt><dd>${escapeHTML(item.data.room)}</dd><dt>Thread</dt><dd>${escapeHTML(item.data.thread)}</dd><dt>Message</dt><dd>${escapeHTML(item.data.message)}</dd></dl><p class="small-note">${escapeHTML(item.data.provenance)}</p>`).join('')}</article>` : '';
  return `<article class="panel"><p class="eyebrow">THE ORIGINAL REPORT</p><h2>What happened?</h2><dl class="facts"><div class="wide"><dt>Reproduction steps</dt><dd>${escapeHTML(c.report.steps || 'Not supplied')}</dd></div><div><dt>Expected behavior</dt><dd>${escapeHTML(c.report.expected || 'Not supplied')}</dd></div><div><dt>Actual behavior</dt><dd>${escapeHTML(c.report.actual || 'Not supplied')}</dd></div><div><dt>Source</dt><dd>${escapeHTML(c.report.source || 'Not supplied')}</dd></div><div><dt>Acceptance policy</dt><dd>${escapeHTML(c.report.policy)}</dd></div></dl></article>${contextPanel}${c.state === 'CLARIFYING' ? `<article class="panel"><h2>Complete the report</h2><p class="muted">Missing: ${escapeHTML(c.missing_fields.join(', '))}</p><form id="clarify-form">${c.missing_fields.map(field => `<label>${escapeHTML(field)}<textarea name="${escapeHTML(field)}" required rows="2"></textarea></label>`).join('')}<button class="primary" type="submit">Save details</button></form></article>` : ''}<article class="panel"><p class="eyebrow">REVISION BINDING</p><h2>The exact code under review</h2><dl><dt>Baseline</dt><dd><code>${escapeHTML(c.baseline?.commit || 'Awaiting reproduction')}</code></dd><dt>Candidate</dt><dd><code>${escapeHTML(c.candidate?.commit || 'No candidate proposed')}</code></dd><dt>Human review</dt><dd>${c.approval ? `${escapeHTML(c.approval.reviewer)} · ${escapeHTML(c.approval.reason)}` : 'No approval recorded'}</dd></dl></article>${response ? `<article class="panel"><p class="eyebrow">CUSTOMER RESPONSE / UNSENT DRAFT</p><h2>Ready for your words</h2><pre class="code-block">${escapeHTML(response.valid ? response.data.content : response.error)}</pre></article>` : ''}`;
}
function timelineHTML(c) {
  return `<article class="panel"><p class="eyebrow">RECORDED EVENTS</p><h2>The trail behind the result</h2><ol class="timeline">${c.events.map(event => `<li><strong>${escapeHTML(event.action.replaceAll('_', ' '))}</strong><time datetime="${escapeHTML(event.at)}">${escapeHTML(date(event.at))}</time>${event.commit ? `<p>Commit ${escapeHTML(event.commit)}</p>` : ''}${event.reviewer ? `<p>${escapeHTML(event.reviewer)}: ${escapeHTML(event.reason)}</p>` : ''}${event.evidence ? `<p>${escapeHTML(event.evidence.path)}</p>` : ''}</li>`).join('')}</ol></article>`;
}
function patchHTML() {
  const {diff, diff_error} = state.view;
  return `<article class="panel"><p class="eyebrow">BASELINE → CANDIDATE</p><h2>What actually changed</h2>${diff_error ? `<p class="form-error">${escapeHTML(diff_error)}</p>` : `<pre class="code-block">${diff ? diff.split('\n').map(line => `<span class="diff-line ${line.startsWith('+') ? 'diff-add' : line.startsWith('-') ? 'diff-remove' : line.startsWith('@@') ? 'diff-hunk' : ''}">${escapeHTML(line)}</span>`).join('') : 'No candidate diff is available yet.'}</pre>`}</article>`;
}

function renderDetail() {
  const c = state.view.case;
  const checks = evidenceFor('verification');
  const passed = checks?.valid ? checks.data.checks.filter(item => item.passed).length : 0;
  const total = checks?.valid ? checks.data.checks.length : 0;
  const invalid = state.view.evidence.some(item => !item.valid);
  const content = state.tab === 'overview' ? overviewHTML(c) : state.tab === 'patch' ? patchHTML() :
    state.tab === 'checks' ? checksHTML(checks, 'Independent candidate checks') + checksHTML(evidenceFor('baseline'), 'Baseline reproduction') : timelineHTML(c);
  $('#detail-view').innerHTML = `<button class="text-button back-button" id="back">← Back to case desk</button><div class="detail-heading"><div><p class="eyebrow">CASE EVIDENCE / ${escapeHTML(c.id)}</p><h1>${escapeHTML(c.report.summary || 'Incomplete report')}</h1></div><button class="secondary" id="export">↓ Export report</button></div><div class="detail-meta">${badge(c.state)}<span class="live-tag">${escapeHTML(c.report.source || 'Source not supplied')}</span><span class="case-id">Updated ${escapeHTML(date(c.updated_at))}</span></div>${invalid ? '<p class="alert" role="alert">One or more evidence files failed integrity checks. Review is blocked until evidence is restored or checks rerun.</p>' : ''}<div class="detail-grid"><div class="detail-main"><div class="tabs" role="tablist" aria-label="Case evidence">${[['overview','Overview'],['patch','Patch'],['checks','Checks'],['timeline','Timeline']].map(([key,label]) => `<button role="tab" id="tab-${key}" class="tab ${state.tab === key ? 'active' : ''}" aria-selected="${state.tab === key}" tabindex="${state.tab === key ? 0 : -1}" aria-controls="case-content" data-tab="${key}">${label}</button>`).join('')}</div><div id="case-content" class="detail-content" role="tabpanel" aria-labelledby="tab-${state.tab}">${content}</div></div><aside class="detail-aside"><article class="panel"><p class="eyebrow">AT A GLANCE</p><h2>Proof, not a promise.</h2><dl><dt>Acceptance checks</dt><dd>${total ? `${passed} / ${total} passed` : 'Awaiting verifier'}</dd><dt>Candidate attempts</dt><dd>${c.total_attempts} recorded</dd><dt>Case elapsed time</dt><dd>${Math.floor(state.view.elapsed_seconds / 60)}m ${state.view.elapsed_seconds % 60}s</dd><dt>Human review decisions</dt><dd>${c.events.filter(e => ['human_approve','human_reject'].includes(e.action)).length}</dd></dl><p class="small-note">Elapsed time spans first to latest event, including waits.</p><button class="secondary" id="copy-handoff">⇄ Copy Switch handoff</button><p class="small-note">Paste into your connected room. This does not send a message.</p></article><article class="panel"><p class="eyebrow">HUMAN CHECKPOINT</p><h2>Your final say.</h2>${c.state === 'VERIFIED' ? `<p class="muted">Inspect the patch and checks before accepting this exact candidate. This records a local operator decision.</p><form id="review-form" class="review-form"><label>Your name<input name="reviewer" required maxlength="150" autocomplete="name"></label><label>What did you review?<textarea name="reason" required rows="3" maxlength="2000"></textarea></label><div class="review-actions"><button class="secondary danger" type="submit" name="decision" value="reject" ${invalid ? 'disabled' : ''}>Reject</button><button class="primary" type="submit" name="decision" value="approve" ${invalid ? 'disabled' : ''}>Accept patch</button></div></form>` : c.state === 'APPROVED' ? `<p class="muted">Accepted by ${escapeHTML(c.approval.reviewer)}. ${escapeHTML(c.approval.reason)}</p><button class="primary" id="draft">${c.response ? 'Regenerate reply draft' : 'Create reply draft'}</button>${c.response ? '<button class="secondary" id="close-case">Close local case</button>' : ''}` : c.state === 'CLOSED' ? '<p class="muted">Local patch accepted and case closed. The reply remains an unsent draft.</p>' : '<p class="muted">A candidate must pass independent checks before it is ready for your decision.</p>'}${['PATCH_READY','VERIFIED','APPROVED'].includes(c.state) ? '<button class="secondary" id="verify">↻ Run independent checks</button><p class="small-note">Rerunning checks clears any prior approval and draft.</p>' : ''}<p class="small-note">No automatic merge or deployment. This local account is not an authenticated reviewer boundary.</p></article></aside></div>`;
  $('#back').addEventListener('click', () => { showPage('desk'); refresh(); });
  document.querySelectorAll('[data-tab]').forEach(button => {
    button.addEventListener('click', () => { state.tab = button.dataset.tab; renderDetail(); $(`#tab-${state.tab}`).focus(); });
    button.addEventListener('keydown', event => {
      const tabs = ['overview','patch','checks','timeline'];
      if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      event.preventDefault();
      const index = tabs.indexOf(state.tab);
      state.tab = event.key === 'Home' ? tabs[0] : event.key === 'End' ? tabs[3] : tabs[(index + (event.key === 'ArrowRight' ? 1 : 3)) % 4];
      renderDetail(); $(`#tab-${state.tab}`).focus();
    });
  });
  $('#export').addEventListener('click', exportReport);
  $('#copy-handoff').addEventListener('click', () => copy(handoff(c)));
  $('#review-form')?.addEventListener('submit', event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    mutate('review', {decision:event.submitter.value,reviewer:form.get('reviewer'),reason:form.get('reason'),
      commit:c.candidate.commit, verification_sha256:c.verification.evidence.sha256});
  });
  $('#clarify-form')?.addEventListener('submit', event => {
    event.preventDefault(); mutate('clarify', {report:Object.fromEntries(new FormData(event.currentTarget))});
  });
  $('#draft')?.addEventListener('click', () => mutate('draft'));
  $('#close-case')?.addEventListener('click', () => mutate('close'));
  $('#verify')?.addEventListener('click', runVerification);
  if (state.busy) $('#detail-view').querySelectorAll('button,input,textarea').forEach(element => { element.disabled = true; });
}

function handoff(c) {
  const baseline = c.baseline ? `Repository: ${c.baseline.repo}\nBaseline: ${c.baseline.commit}\n` : 'Supply the actual baseline-only repository path and full commit SHA.\n';
  return `@proofdesk-concierge Continue existing case ${c.id}; do not create a duplicate.\nReport: ${c.report.summary}\nSteps: ${c.report.steps}\nExpected: ${c.report.expected}\nActual: ${c.report.actual}\n${baseline}Current candidate: ${c.candidate?.commit || 'none'}\nRead agents/concierge.md and docs/demo.md. Use the shared project .proofdesk store. Collect the real room/thread references. Ask Builder to reproduce and prepare a committed patch, then have Verifier run the trusted checks. Do not use prepared candidate fixtures or approve on my behalf. Return the exact candidate and evidence for human review. Replace this mention if your configured prefix differs.`;
}
async function mutate(action, data = {}) {
  if (state.busy) return;
  state.busy = true; clearError(); renderDetail();
  try {
    await api(`/api/cases/${state.selected}/${action}`, data);
    state.view = await api(`/api/cases/${state.selected}`);
    toast(action === 'review' ? 'Your decision was recorded against this revision.' : 'Case updated.');
  } catch (error) { alertError(error); }
  finally { state.busy = false; renderDetail(); await refresh(); }
}
async function runVerification() {
  if (state.busy) return;
  state.busy = true; clearError(); renderDetail();
  try {
    const job = await api(`/api/cases/${state.selected}/verify`, {});
    state.job = job.id;
    toast('Independent checks are running.');
    let result = job;
    while (['queued','running'].includes(result.status)) {
      await new Promise(resolve => setTimeout(resolve, 900));
      result = await api(`/api/jobs/${job.id}`);
    }
    if (result.status === 'failed') throw new Error(result.error);
    state.view = await api(`/api/cases/${state.selected}`);
    toast(result.state === 'VERIFIED' ? 'Checks passed. Ready for human review.' : `Checks finished: ${labels[result.state] || result.state}`);
    state.tab = 'checks';
  } catch (error) { alertError(error); }
  finally { state.busy = false; state.job = null; renderDetail(); await refresh(); }
}
async function exportReport() {
  try {
    const response = await fetch(`/api/cases/${state.selected}/export`, {headers:{Authorization:`Bearer ${token}`}});
    if (!response.ok) throw new Error((await response.json()).error);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a'); link.href = url; link.download = `${state.selected}.html`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast('Report exported. Review local paths before sharing.');
  } catch (error) { alertError(error); }
}
async function copy(text) {
  try { await navigator.clipboard.writeText(text); toast('Copied to clipboard.'); }
  catch { alertError(new Error('Clipboard unavailable. Use the documented request in docs/demo.md.')); }
}
function openNewCase() {
  $('#case-form').reset(); $('#form-error').hidden = true;
  $('#case-dialog').showModal();
}
$('#case-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const button = $('button[type="submit"]', event.currentTarget);
  button.disabled = true; $('#form-error').hidden = true;
  try {
    const report = {policy:'order-total-v1'};
    for (const key of ['summary','steps','expected','actual','source']) report[key] = form.get(key).trim();
    const c = await api('/api/cases', {request_key:form.get('request_key').trim(),report});
    $('#case-dialog').close(); await refresh(); await openCase(c.id); toast('Case created. Copy its handoff into Switch to start the agents.');
  } catch (error) { $('#form-error').textContent = error.message; $('#form-error').hidden = false; }
  finally { button.disabled = false; }
});
$('#new-case').addEventListener('click', openNewCase);
$('#close-dialog').addEventListener('click', () => $('#case-dialog').close());
$('#nav-cases').addEventListener('click', () => { showPage('desk'); refresh(); });
$('#nav-connection').addEventListener('click', () => { showPage('setup'); loadHealth(); });
$('#refresh').addEventListener('click', () => { clearError(); refresh(); });
$('#search').addEventListener('input', renderCases);
$('#filter').addEventListener('change', renderCases);
$('#copy-prepare').addEventListener('click', () => copy('python -m scripts.live'));
async function loadHealth() {
  try {
    const health = await api('/api/health');
    $('#health-details').innerHTML = `<dt>Python</dt><dd>${escapeHTML(health.python)}</dd><dt>Git executable</dt><dd>${health.git_available ? 'Available' : 'Not found on server PATH'}</dd><dt>Switch / provider</dt><dd>Requires verification in Console</dd><dt>Data source</dt><dd>Local case store · live reads</dd>`;
  } catch (error) { alertError(error); }
}
refresh();
setInterval(() => { if (!document.hidden && !$('#case-dialog').open && !state.busy) refresh({detail:true}); }, 5000);
