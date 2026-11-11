import { useEffect, useState } from "react";
import { AlertCircle, Brain, Download, FileText, LoaderCircle, Sparkles, Target, TrendingUp, UploadCloud, Workflow } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

function ResultList({ title, icon, items = [] }) {
  return <><h3>{icon}{title}</h3>{items.length ? <ul>{items.map((item, i) => <li key={i}>{item}</li>)}</ul> : <p>None identified.</p>}</>;
}

const agentLabels = {
  strategist: "Sales Strategist",
  critic: "Pitch Critic",
  sales_coach: "Sales Coach",
  report_synthesizer: "Report Synthesizer",
};

export default function App() {
  const [file, setFile] = useState(null);
  const [provider, setProvider] = useState("openai");
  const [competitors, setCompetitors] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [industry, setIndustry] = useState("");
  const [researchMode, setResearchMode] = useState("both");
  const [competitiveResearch, setCompetitiveResearch] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState("");
  const [exportMessage, setExportMessage] = useState("");
  const [token, setToken] = useState(() => localStorage.getItem("pitchintel_token") || "");
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [history, setHistory] = useState([]);

  async function authenticate(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await fetch(`${API_URL}/auth/${authMode === "register" ? "register" : "login"}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: authEmail, password: authPassword, full_name: fullName }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Authentication failed");
      localStorage.setItem("pitchintel_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      setAuthPassword("");
    } catch (err) { setError(err.message); }
  }

  function logout() {
    localStorage.removeItem("pitchintel_token");
    setToken(""); setUser(null); setHistory([]);
    setResult(null); setCompetitiveResearch(null);
  }

  async function loadHistory(accessToken = token) {
    if (!accessToken) return;
    const response = await fetch(`${API_URL}/history`, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (response.ok) { const data = await response.json(); setHistory(data.items || []); }
    else if (response.status === 401) logout();
  }

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => { if (!response.ok) throw new Error("Session expired"); return response.json(); })
      .then((data) => { setUser(data); loadHistory(token); })
      .catch(() => logout());
  }, [token]);

  async function analyzePitch(event) {
    event.preventDefault();
    if (!file) { setError("Please upload a sales pitch first."); return; }
    if (!companyName.trim()) { setError("Please enter your company or product name for competitive research."); return; }
    setLoading(true); setError(""); setResult(null); setWorkflow(null); setCompetitiveResearch(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("provider", provider);
    formData.append("competitors", competitors);
    try {
      const response = await fetch(`${API_URL}/agent-workflow`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Agent workflow failed");
      setResult(data.analysis);
      setWorkflow(data.workflow);
      const researchResponse = await fetch(`${API_URL}/competitive-research`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ company_name: companyName, industry, competitors: competitors.split(",").map((v) => v.trim()).filter(Boolean), research_mode: researchMode, provider }),
      });
      const researchData = await researchResponse.json();
      if (!researchResponse.ok) throw new Error(researchData.detail || "Competitor research failed");
      setCompetitiveResearch(researchData.research);
      const saved = await fetch(`${API_URL}/history`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ company_name: companyName, source_filename: file.name, analysis: data.analysis, competitive_research: researchData.research }) });
      if (!saved.ok) throw new Error("Analysis completed, but saving to history failed.");
      await loadHistory();
    } catch (err) {
      setError(err.message || "Unable to reach the backend. Is it running?");
    } finally { setLoading(false); }
  }

  async function exportReport(format) {
    if (!result) return;
    setExporting(format);
    setExportMessage("");
    setError("");
    try {
      const response = await fetch(`${API_URL}/reports/${format}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          company_name: companyName || "Sales Pitch Review",
          source_filename: file?.name || null,
          analysis: result,
          competitive_research: competitiveResearch,
          workflow,
        }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `Unable to generate ${format.toUpperCase()} report`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${(companyName || "PitchIntel").replace(/[^A-Za-z0-9_-]+/g, "-")}-PitchIntel-Report.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setExportMessage(`${format.toUpperCase()} report downloaded.`);
    } catch (err) {
      setError(err.message || "Report export failed");
    } finally {
      setExporting("");
    }
  }

  const scoreClass = (score) => score >= 80 ? "good" : score >= 60 ? "average" : "poor";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><Brain size={24} /></div><div><strong>PitchIntel AI</strong><span>Multi-Agent Sales Intelligence</span></div></div>
        <div className="workspace-pill"><i /> {user?.email || "Secure Workspace"} <button className="logout-button" onClick={logout}>Sign out</button></div>
      </header>
      <main className="container">
        <section className="hero">
          <span className="eyebrow"><Sparkles size={15} /> MULTI-AGENT SALES ANALYSIS</span>
          <h1>Turn your sales pitch into<br /><em>a competitive advantage.</em></h1>
          <p>Four specialised AI agents collaborate to evaluate your messaging, uncover gaps and create a stronger sales pitch.</p>
        </section>
        <section className="history-strip"><div><b>Saved analyses</b><span>{history.length} reports in your account</span></div><button type="button" onClick={() => loadHistory()}>Refresh history</button>{history.slice(0,5).map((item) => <button type="button" className="history-item" key={item.id} onClick={() => {setResult(item.analysis);setCompetitiveResearch(item.competitive_research);setCompanyName(item.company_name);}}><b>{item.company_name}</b><span>{item.overall_score}/100 · {new Date(item.created_at).toLocaleDateString()}</span></button>)}</section>
        <section className="workspace">
          <form className="panel" onSubmit={analyzePitch}>
            <div className="panel-heading"><div><span className="step">01</span><h2>Upload your sales pitch</h2></div><FileText /></div>
            <label className="upload-area">
              <UploadCloud size={36} />
              <strong>{file ? file.name : "Choose a presentation to analyse"}</strong>
              <span>PDF, PPTX or DOCX · Max 20 MB</span>
              <input type="file" accept=".pdf,.pptx,.docx" onChange={(e) => { setFile(e.target.files?.[0] || null); setError(""); setResult(null); setWorkflow(null); }} />
            </label>
            <label className="field-label" htmlFor="provider">AI model</label>
            <select id="provider" value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="openai">OpenAI</option><option value="gemini">Google Gemini</option>
            </select>
            <label className="field-label" htmlFor="companyName">Your company / product <span>Required for competitor research</span></label>
            <input id="companyName" value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="e.g. Acme CRM" />
            <label className="field-label" htmlFor="industry">Industry</label>
            <input id="industry" value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="e.g. CRM software" />
            <label className="field-label" htmlFor="competitors">Competitors <span>Comma-separated · optional in automatic mode</span></label>
            <input id="competitors" value={competitors} onChange={(e) => setCompetitors(e.target.value)} placeholder="e.g. Salesforce, HubSpot, Zoho" />
            <label className="field-label" htmlFor="researchMode">Competitor research mode</label>
            <select id="researchMode" value={researchMode} onChange={(e) => setResearchMode(e.target.value)}>
              <option value="both">Automatic discovery + my competitors</option><option value="automatic">Automatic discovery only</option><option value="manual">My competitor list only</option>
            </select>
            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? <><LoaderCircle className="spin" size={18} /> Running pitch agents + competitor research…</> : <><Sparkles size={18} /> Run agentic pitch review</>}
            </button>
            <p className="privacy-note">The temporary upload is deleted after processing. Document content is sent to the selected AI provider. Phase 3 uses live web search. Add TAVILY_API_KEY to the backend environment. Search and AI provider usage may incur charges.</p>
            {error && <div className="error"><AlertCircle size={17} />{error}</div>}
          </form>
          <section className="panel results-panel">
            <div className="panel-heading"><div><span className="step">02</span><h2>Agent analysis results</h2></div><Workflow /></div>
            {!result && !loading && <div className="empty-state"><div className="empty-icon"><FileText size={32} /></div><h3>Your report will appear here</h3><p>Upload a sales pitch to start the LangGraph multi-agent workflow.</p></div>}
            {loading && <div className="empty-state"><LoaderCircle className="spin" size={36} /><h3>Agents are collaborating</h3><p>The strategist, critic, coach and report synthesizer are processing your pitch.</p></div>}
            {result && <div className="results">
              {workflow && <><h3><Workflow size={17} /> Completed workflow</h3><div className="agent-trace">{workflow.completed_agents.map((agent, index) => <div className="agent-step" key={agent}><span>{String(index + 1).padStart(2, "0")}</span><b>{agentLabels[agent] || agent}</b><small>Completed</small></div>)}</div></>}
              <div className="score-card"><div><span>Overall pitch score</span><small>Multi-agent assessment · /100</small></div><strong className={scoreClass(result.overall_score)}>{result.overall_score}<small>/100</small></strong></div>
              <h3>Executive summary</h3><p>{result.executive_summary}</p>
              <h3>Performance metrics</h3>
              {[[ "Messaging quality", result.messaging_quality ], [ "Value proposition", result.value_proposition ], [ "Target audience clarity", result.target_audience_clarity ], [ "Call to action", result.call_to_action ]].map(([name, score]) => (
                <div className="metric" key={name}><div><span>{name}</span><b>{score}/100</b></div><progress value={score} max="100" /></div>
              ))}
              <ResultList title="Strengths" icon={<TrendingUp size={17} />} items={result.strengths} />
              <ResultList title="Weaknesses and risks" icon={<AlertCircle size={17} />} items={result.weaknesses} />
              <ResultList title="Missing information" items={result.missing_information} />
              <ResultList title="Recommendations" icon={<Target size={17} />} items={result.recommendations} />
              <h3>Improved sales pitch</h3><div className="improved-pitch">{result.improved_pitch}</div>
              <h3>Competitor context</h3><p>{result.competitor_context}</p>
              {competitiveResearch && <section className="competitive-report">
                <h3><Target size={17} /> Live competitive intelligence</h3>
                <p>{competitiveResearch.market_overview}</p>
                <div className="competitor-chips">{competitiveResearch.competitors_researched.map((name) => <span key={name}>{name}</span>)}</div>
                <ResultList title="Competitive themes" items={competitiveResearch.competitive_themes} />
                <ResultList title="Pitch opportunities" items={competitiveResearch.pitch_opportunities} />
                {competitiveResearch.findings.map((finding) => <article className="competitor-card" key={finding.name}>
                  <h4>{finding.name} <small>{finding.confidence} confidence</small></h4><p>{finding.summary}</p><p><b>Positioning:</b> {finding.positioning}</p>
                  <ResultList title="Products and features" items={finding.products_and_features} />
                  <ResultList title="Pricing observations" items={finding.pricing_observations} />
                  <ResultList title="Differentiators" items={finding.differentiators} />
                  {finding.caveats?.length > 0 && <ResultList title="Caveats" items={finding.caveats} />}
                  <small>Sources: {finding.source_ids.join(", ") || "None linked"}</small>
                </article>)}
                <h3>Research sources</h3>
                <ol className="source-list">{competitiveResearch.sources.map((source) => <li key={source.source_id}><b>{source.source_id}</b> · <a href={source.url} target="_blank" rel="noreferrer">{source.title || source.url}</a><p>{source.snippet}</p></li>)}</ol>
                <p className="disclaimer">{competitiveResearch.evidence_policy}</p>
              </section>}
              <section className="export-panel">
                <h3><Download size={17} /> Download your report</h3>
                <p>Choose a format. Reports include the pitch assessment and competitor research when available.</p>
                <div className="export-actions">
                  {["pdf", "docx", "pptx"].map((format) => <button type="button" key={format} onClick={() => exportReport(format)} disabled={Boolean(exporting)}>
                    {exporting === format ? <LoaderCircle className="spin" size={15} /> : <Download size={15} />} {format.toUpperCase()}
                  </button>)}
                </div>
                {exportMessage && <p className="export-success">{exportMessage}</p>}
              </section>
              <p className="disclaimer">AI-generated assessment. Review source pages before relying on competitive claims or pricing.</p>
            </div>}
          </section>
        </section>
        <footer>PitchIntel AI · Phase 3 · Multi-agent + live competitive intelligence</footer>
      </main>
    </div>
  );
}
