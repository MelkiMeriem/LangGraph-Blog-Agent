import { useEffect, useState } from "react";
import { fetchLanguages } from "../api";

export default function GenerateForm({ onGenerate, loading }) {
  const [inputType, setInputType] = useState("topic");
  const [content, setContent] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("");
  const [languages, setLanguages] = useState([]);

  useEffect(() => {
    fetchLanguages()
      .then(setLanguages)
      .catch(() => setLanguages([]));
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    onGenerate({
      input_type: inputType,
      content,
      target_language: targetLanguage || null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-ink/10 pt-10">
      <div className="mb-8 flex gap-6 text-sm">
        {["topic", "youtube"].map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setInputType(type)}
            className={`relative pb-2 font-medium uppercase tracking-wide transition-colors ${
              inputType === type ? "text-ink" : "text-ink/40 hover:text-ink/70"
            }`}
          >
            {type === "topic" ? "Topic" : "YouTube URL"}
            {inputType === type && <span className="absolute inset-x-0 -bottom-px h-px bg-accent" />}
          </button>
        ))}
      </div>

      <div className="mb-8">
        <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-ink/50">
          {inputType === "topic" ? "Blog topic" : "YouTube video URL"}
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={inputType === "topic" ? 3 : 1}
          placeholder={
            inputType === "topic" ? "e.g. The history of coffee" : "https://www.youtube.com/watch?v=..."
          }
          className="w-full resize-none border-b border-ink/15 bg-transparent py-2 font-serif text-lg text-ink placeholder:text-ink/30 focus:border-accent focus:outline-none"
        />
      </div>

      <div className="mb-10">
        <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-ink/50">
          Translate to
        </label>
        <select
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
          className="w-full border-b border-ink/15 bg-transparent py-2 text-sm text-ink focus:border-accent focus:outline-none"
        >
          <option value="">No translation</option>
          {languages.map((lang) => (
            <option key={lang} value={lang}>
              {lang.charAt(0).toUpperCase() + lang.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="inline-flex items-center gap-2 bg-accent px-6 py-3 text-sm font-medium uppercase tracking-wide text-paper transition-colors hover:bg-accent-dark disabled:cursor-not-allowed disabled:bg-ink/20"
      >
        {loading && (
          <span className="h-3 w-3 animate-spin rounded-full border-2 border-paper/40 border-t-paper" />
        )}
        {loading ? "Generating" : "Generate blog post"}
      </button>
    </form>
  );
}
