import { useState } from "react";
import { AlertCircle, Brain, FileText, LoaderCircle, Sparkles, Target, TrendingUp, UploadCloud } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

function ResultList({ title, icon, items = [] }) {
  return <><h3>{icon}{title}</h3>{items.length ? <ul>{items.map((item, i) => <li key={i}>{item}</li>)}</ul> : <p>None identified.</p>}</>;
}

export default function App() {
  const [file, setFile] = useState(null);
  const [provider, setProvider] = useState("openai");
  const [competitors, setCompetitors] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function analyzePitch(event) {
    event.preventDefault();
    if (!file) { setError("Please upload a sales pitch first."); return; }
    setLoading(true); setError(""); setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("provider", provider);
    formData.append("competitors", competitors);
    try {
      const response = await fetch(`${API_URL}/analyze`, { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Analysis failed");
      setResult(data.analysis);
    } catch (err) {
      setError(err.message || "Unable to reach the backend. Is it running?");
    } finally { setLoading(false); }
  }

  const scoreClass = (score) => score >= 80 ? "good" : score >= 60 ? "average" : "poor";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><Brain size={24} /></div><div><strong>PitchIntel AI</strong><span>Sales Intelligence Workspace</span></div></div>
        <div className="workspace-pill"><i /> AI Workspace</div>
      </header>
      <main className="container">
        <section className="hero">
          <span className="eyebrow"><Sparkles size={15} /> INTELLIGENT SALES ANALYSIS</span>
          <h1>Turn your sales pitch into<br /><em>a competitive advantage.</em></h1>
          <p>Review your messaging, uncover gaps and prepare a stronger pitch with AI-powered analysis.</p>
        </section>
        <section className="workspace">
          <form className="panel" onSubmit={analyzePitch}>
            <div className="panel-heading"><div><span className="step">01</span><h2>Upload your sales pitch</h2></div><FileText /></div>
            <label className="upload-area">
              <UploadCloud size={36} />
              <strong>{file ? file.name : "Choose a presentation to analyse"}</strong>
              <span>PDF, PPTX or DOCX · Max 20 MB</span>
              <input type="file" accept=".pdf,.pptx,.docx" onChange={(e) => { setFile(e.target.files?.[0] || null); setError(""); setResult(null); }} />
            </label>
            <label className="field-label" htmlFor="provider">AI model</label>
            <select id="provider" value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="openai">OpenAI</option><option value="gemini">Google Gemini</option>
            </select>
            <label className="field-label" htmlFor="competitors">Competitors <span>Optional</span></label>
            <input id="competitors" value={competitors} onChange={(e) => setCompetitors(e.target.value)} placeholder="e.g. Salesforce, HubSpot, Zoho" />
            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? <><LoaderCircle className="spin" size={18} /> Analysing pitch…</> : <><Sparkles size={18} /> Analyse sales pitch</>}
            </button>
            <p className="privacy-note">The temporary upload is deleted after processing. Document content is sent to the selected AI provider.</p>
            {error && <div className="error"><AlertCircle size={17} />{error}</div>}
          </form>
          <section className="panel results-panel">
            <div className="panel-heading"><div><span className="step">02</span><h2>Analysis results</h2></div><TrendingUp /></div>
            {!result && !loading && <div className="empty-state"><div className="empty-icon"><FileText size={32} /></div><h3>Your report will appear here</h3><p>Upload a sales pitch and run your first analysis to see the findings.</p></div>}
            {loading && <div className="empty-state"><LoaderCircle className="spin" size={36} /><h3>Reviewing your presentation</h3><p>Extracting content and evaluating the sales narrative.</p></div>}
            {result && <div className="results">
              <div className="score-card"><div><span>Overall pitch score</span><small>AI assessment · /100</small></div><strong className={scoreClass(result.overall_score)}>{result.overall_score}<small>/100</small></strong></div>
              <h3>Executive summary</h3><p>{result.executive_summary}</p>
              <h3>Performance metrics</h3>
              {[["Messaging quality", result.messaging_quality], ["Value proposition", result.value_proposition], ["Target audience clarity", result.target_audience_clarity], ["Call to action", result.call_to_action]].map(([name, score]) => (
                <div className="metric" key={name}><div><span>{name}</span><b>{score}/100</b></div><progress value={score} max="100" /></div>
              ))}
              <ResultList title="Strengths" icon={<TrendingUp size={17} />} items={result.strengths} />
              <ResultList title="Weaknesses" icon={<AlertCircle size={17} />} items={result.weaknesses} />
              <ResultList title="Missing information" items={result.missing_information} />
              <ResultList title="Recommendations" icon={<Target size={17} />} items={result.recommendations} />
              <h3>Improved sales pitch</h3><div className="improved-pitch">{result.improved_pitch}</div>
              <h3>Competitor context</h3><p>{result.competitor_context}</p>
              <p className="disclaimer">AI-generated assessment, not independently verified market research. Competitor names were supplied by the user.</p>
            </div>}
          </section>
        </section>
        <footer>PitchIntel AI · Phase 1 foundation</footer>
      </main>
    </div>
  );
}
