import { useMemo, useState } from 'react'
import { FileText, Mail, ShieldCheck, Sparkles, UploadCloud } from 'lucide-react'
import { triageEmail } from './api'

const initial = {
  sender: 'customer@example.com',
  subject: 'Unable to access my account',
  body: 'I reset my password twice but I still cannot login. Please help.',
}

function App() {
  const [form, setForm] = useState(initial)
  const [files, setFiles] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const priorityClass = useMemo(() => {
    const value = result?.decision?.priority || ''
    return `pill ${value}`
  }, [result])

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      setResult(await triageEmail({ ...form, files }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <span className="eyebrow"><Sparkles size={15} /> Agentic AI Portfolio Demo</span>
          <h1>Multimodal Email Triage</h1>
          <p>Azure Document Intelligence + Qdrant Cloud + Azure Foundry, orchestrated by FastAPI.</p>
        </div>
        <div className="status-card"><ShieldCheck size={20} /><div><strong>Cloud-assisted</strong><span>Lightweight EC2 runtime</span></div></div>
      </header>

      <section className="grid">
        <form className="panel" onSubmit={submit}>
          <div className="panel-title"><Mail size={19} /><h2>Email input</h2></div>
          <label>Sender<input value={form.sender} onChange={e => setForm({ ...form, sender: e.target.value })} /></label>
          <label>Subject<input required value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} /></label>
          <label>Body<textarea required rows="9" value={form.body} onChange={e => setForm({ ...form, body: e.target.value })} /></label>
          <label className="upload"><UploadCloud size={22} /><span>Attach PDF or image</span><input type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.bmp,.txt,.md" onChange={e => setFiles(Array.from(e.target.files || []))} /></label>
          {files.length > 0 && <div className="file-list">{files.map(file => <span key={file.name}>{file.name}</span>)}</div>}
          <button disabled={loading}>{loading ? 'Processing…' : 'Run triage'}</button>
          {error && <div className="error">{error}</div>}
        </form>

        <section className="panel results">
          <div className="panel-title"><FileText size={19} /><h2>Agent result</h2></div>
          {!result ? <div className="empty">Run an email through the pipeline to see the decision trace, evidence and grounded reply.</div> : <>
            <div className="decision-grid">
              <div><span>Category</span><strong>{result.decision.category}</strong></div>
              <div><span>Priority</span><strong className={priorityClass}>{result.decision.priority}</strong></div>
              <div><span>Language</span><strong>{result.decision.language}</strong></div>
              <div><span>Human review</span><strong>{result.decision.human_review_required ? 'Required' : 'No'}</strong></div>
            </div>
            <div className="block"><h3>Processing trace</h3><div className="trace">{result.trace.map(step => <span key={step}>✓ {step}</span>)}</div></div>
            <div className="block"><h3>Retrieved evidence</h3>{result.retrieved_context.length ? result.retrieved_context.map(item => <article key={`${item.source}-${item.score}`}><strong>{item.source}</strong><p>{item.text}</p></article>) : <p className="muted">No retrieval was required.</p>}</div>
            <div className="block reply"><h3>Grounded reply</h3><p>{result.draft_reply}</p></div>
          </>}
        </section>
      </section>
    </main>
  )
}

export default App
