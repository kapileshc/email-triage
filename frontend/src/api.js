const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function triageEmail({ sender, subject, body, files }) {
  const form = new FormData()
  form.append('sender', sender)
  form.append('subject', subject)
  form.append('body', body)
  for (const file of files) form.append('files', file)

  const response = await fetch(`${API_BASE}/api/triage-with-files`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const payload = await response.json()
      message = payload.detail || message
    } catch (_) {}
    throw new Error(message)
  }
  return response.json()
}
