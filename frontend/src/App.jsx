import { useMemo, useRef, useState } from 'react'
import {
  AlertCircle, ArrowRight, Check, CheckCircle2, ChevronRight, Clipboard,
  File, FileSearch, Inbox, LoaderCircle, Mail, RotateCcw, ShieldCheck,
  Sparkles, Trash2, UploadCloud,
} from 'lucide-react'
import { triageEmail } from './api'

const initial = {
  sender: 'customer@example.com',
  subject: 'Unable to access my account',
  body: 'I reset my password twice but I still cannot login. Please help.',
}

const friendlyTrace = {
  language_detected: 'Language detected',
  triage_completed: 'Email classified',
  attachments_processed: 'Attachments processed',
  knowledge_retrieved: 'Knowledge retrieved',
  reply_generated: 'Reply drafted',
}

function formatLabel(value = '') {
  return value.replaceAll('_', ' ').replace(/\b\w/g, letter => letter.toUpperCase())
}

function formatTrace(value) {
  const [key, detail] = value.split(':')
  return detail ? `${friendlyTrace[key] || formatLabel(key)} · ${formatLabel(detail)}` : friendlyTrace[key] || formatLabel(key)
}

function App() {
  const [form, setForm] = useState(initial)
  const [files, setFiles] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const fileInput = useRef(null)

  const priorityClass = useMemo(() => `priority-badge ${result?.decision?.priority || ''}`, [result])

  function updateField(field, value) {
    setForm(current => ({ ...current, [field]: value }))
  }

  function resetForm() {
    setForm({ sender: '', subject: '', body: '' })
    setFiles([])
    setResult(null)
    setError('')
    if (fileInput.current) fileInput.current.value = ''
  }

  function removeFile(index) {
    setFiles(current => current.filter((_, fileIndex) => fileIndex !== index))
  }

  async function copyReply() {
    if (!result?.draft_reply) return
    await navigator.clipboard.writeText(result.draft_reply)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1800)
  }

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setCopied(false)
    try {
      setResult(await triageEmail({ ...form, files }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-frame">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Triage workspace home">
          <span className="brand-mark"><Inbox size={20} /></span>
          <span><strong>Triage</strong><small>AI email operations</small></span>
        </a>
        <div className="system-status"><span className="status-dot" /> Systems operational</div>
      </header>

      <main className="shell">
        <header className="page-heading">
          <div>
            <span className="eyebrow"><Sparkles size={14} /> Intelligent routing workspace</span>
            <h1>Understand every email.<br />Route it with confidence.</h1>
            <p>Analyze the message and its attachments, identify the right priority, and create a grounded response in one pass.</p>
          </div>
          <div className="trust-card">
            <ShieldCheck size={20} />
            <div><strong>Review stays in your hands</strong><span>High-risk messages are automatically flagged.</span></div>
          </div>
        </header>

        <div className="stepper" aria-label="Triage workflow">
          <div className="step active"><span>1</span><div><strong>Add email</strong><small>Message and files</small></div></div>
          <ChevronRight size={16} />
          <div className={`step ${loading ? 'active' : result ? 'complete' : ''}`}><span>{result ? <Check size={14} /> : '2'}</span><div><strong>Analyze</strong><small>Classify and retrieve</small></div></div>
          <ChevronRight size={16} />
          <div className={`step ${result ? 'active' : ''}`}><span>3</span><div><strong>Review</strong><small>Decision and reply</small></div></div>
        </div>

        <section className="workspace">
          <form className="panel composer" onSubmit={submit}>
            <div className="panel-header">
              <div className="panel-title"><span className="icon-box"><Mail size={18} /></span><div><h2>Incoming email</h2><p>Enter the message exactly as it was received.</p></div></div>
              <button className="text-button" type="button" onClick={resetForm}><RotateCcw size={14} /> Clear</button>
            </div>

            <div className="field">
              <label htmlFor="sender">Sender</label>
              <input id="sender" type="email" placeholder="name@company.com" value={form.sender} onChange={e => updateField('sender', e.target.value)} />
              <span className="helper">Optional · Helps add context to the analysis</span>
            </div>
            <div className="field">
              <label htmlFor="subject">Subject <span>Required</span></label>
              <input id="subject" required placeholder="What is the email about?" value={form.subject} onChange={e => updateField('subject', e.target.value)} />
            </div>
            <div className="field">
              <div className="label-row"><label htmlFor="body">Message <span>Required</span></label><small>{form.body.length} characters</small></div>
              <textarea id="body" required rows="8" placeholder="Paste the full email message here…" value={form.body} onChange={e => updateField('body', e.target.value)} />
            </div>

            <div className="attachment-section">
              <div className="section-label"><span>Attachments</span><small>Optional</small></div>
              <label className="upload" htmlFor="attachments">
                <span className="upload-icon"><UploadCloud size={21} /></span>
                <span><strong>Choose files</strong> to attach<small>PDF, image, text, or Markdown files</small></span>
                <input ref={fileInput} id="attachments" type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.bmp,.txt,.md" onChange={e => setFiles(Array.from(e.target.files || []))} />
              </label>
              {files.length > 0 && <div className="file-list">{files.map((file, index) => <div key={`${file.name}-${index}`}><File size={15} /><span><strong>{file.name}</strong><small>{Math.max(1, Math.round(file.size / 1024))} KB</small></span><button type="button" onClick={() => removeFile(index)} aria-label={`Remove ${file.name}`}><Trash2 size={14} /></button></div>)}</div>}
            </div>

            {error && <div className="error" role="alert"><AlertCircle size={17} /><div><strong>We couldn’t analyze this email</strong><span>{error}</span></div></div>}
            <button className="primary-button" disabled={loading}>
              {loading ? <><LoaderCircle className="spin" size={17} /> Analyzing email…</> : <>Analyze email <ArrowRight size={17} /></>}
            </button>
            <p className="submit-note"><ShieldCheck size={13} /> Your content is used only to complete this analysis.</p>
          </form>

          <section className="panel results" aria-live="polite" aria-busy={loading}>
            <div className="panel-header">
              <div className="panel-title"><span className="icon-box"><FileSearch size={18} /></span><div><h2>Analysis</h2><p>Classification, rationale, and suggested response.</p></div></div>
              {result && <span className="complete-badge"><CheckCircle2 size={14} /> Complete</span>}
            </div>

            {loading ? (
              <div className="loading-state"><span className="loader"><LoaderCircle className="spin" size={25} /></span><h3>Reviewing the email</h3><p>We’re classifying the request, checking attachments, and gathering relevant context.</p><div className="loading-line"><span /></div></div>
            ) : !result ? (
              <div className="empty-state">
                <span className="empty-illustration"><FileSearch size={30} /><Sparkles size={15} /></span>
                <h3>Your analysis will appear here</h3>
                <p>Complete the email form and select <strong>Analyze email</strong> to see:</p>
                <ul><li><Check size={14} /> Category and priority</li><li><Check size={14} /> Decision rationale</li><li><Check size={14} /> Evidence and a draft reply</li></ul>
              </div>
            ) : <>
              <div className="decision-callout">
                <div><span>Recommended action</span><h3>{result.decision.human_review_required ? 'Send for human review' : 'Ready for standard handling'}</h3><p>{result.decision.reason}</p></div>
                <span className={priorityClass}>{formatLabel(result.decision.priority)} priority</span>
              </div>

              <div className="decision-grid">
                <div><span>Category</span><strong>{formatLabel(result.decision.category)}</strong></div>
                <div><span>Language</span><strong>{formatLabel(result.decision.language)}</strong></div>
                <div><span>Human review</span><strong>{result.decision.human_review_required ? 'Required' : 'Not required'}</strong></div>
                <div><span>Attachments</span><strong>{files.length ? `${files.length} processed` : 'None'}</strong></div>
              </div>

              <div className="result-section">
                <div className="section-heading"><div><h3>Processing activity</h3><p>Checks completed during this analysis</p></div></div>
                <div className="trace">{result.trace.map((step, index) => <div key={`${step}-${index}`}><Check size={12} /><span>{formatTrace(step)}</span></div>)}</div>
              </div>

              <div className="result-section">
                <div className="section-heading"><div><h3>Supporting evidence</h3><p>Knowledge used to inform the response</p></div><span>{result.retrieved_context.length} sources</span></div>
                {result.retrieved_context.length ? <div className="evidence-list">{result.retrieved_context.map((item, index) => <article key={`${item.source}-${index}`}><div><span>{index + 1}</span><strong>{item.source}</strong>{item.score != null && <small>{Math.round(item.score * 100)}% match</small>}</div><p>{item.text}</p></article>)}</div> : <div className="no-evidence">No external knowledge was needed for this message.</div>}
              </div>

              <div className="reply-card">
                <div className="reply-header"><div><h3>Suggested reply</h3><p>Review and personalize before sending.</p></div><button type="button" onClick={copyReply} disabled={!result.draft_reply}>{copied ? <Check size={14} /> : <Clipboard size={14} />}{copied ? 'Copied' : 'Copy'}</button></div>
                <div className="reply-body">{result.draft_reply || <span className="muted">No reply was generated for this message.</span>}</div>
              </div>
            </>}
          </section>
        </section>
      </main>
    </div>
  )
}

export default App
