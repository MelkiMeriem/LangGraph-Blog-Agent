import { useState } from "react";
import { generateBlog, transcribeUpload } from "./api";
import GenerateForm from "./components/GenerateForm.jsx";
import ResultView from "./components/ResultView.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleGenerate(payload) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let finalPayload = payload;
      if (payload.input_type === "upload") {
        const transcript = await transcribeUpload(payload.file);
        finalPayload = {
          input_type: "topic",
          content: transcript,
          target_language: payload.target_language,
        };
      }
      const data = await generateBlog(finalPayload);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper text-ink">
      <div className="mx-auto max-w-2xl px-6 py-16 sm:py-20">
        <header className="mb-12 text-center">
          <p className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-accent">
            Autonomous Content Studio
          </p>
          <h1 className="font-serif text-4xl font-medium tracking-tight text-ink sm:text-5xl">
            Blog Generation Agent
          </h1>
          <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-ink/60">
            Turn a topic, a YouTube video, or an uploaded video/audio file into a finished blog post — with
            optional translation.
          </p>
          <div className="mx-auto mt-8 h-px w-16 bg-accent/40" />
        </header>

        <GenerateForm onGenerate={handleGenerate} loading={loading} />
        <ErrorBanner message={error} />
        {result && <ResultView result={result} />}
      </div>
    </div>
  );
}
