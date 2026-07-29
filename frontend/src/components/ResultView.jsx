import ReactMarkdown from "react-markdown";

export default function ResultView({ result }) {
  const { video_id, titles, selected_title, blog_content, target_language, translated_title, translated_content } =
    result;

  return (
    <div className="mt-14 space-y-14">
      {video_id && (
        <p className="text-xs font-medium uppercase tracking-wide text-ink/40">
          Source — YouTube video {video_id}
        </p>
      )}

      <section>
        <h2 className="mb-3 text-xs font-medium uppercase tracking-wide text-ink/40">Candidate titles</h2>
        <ul className="space-y-1.5 font-serif text-base">
          {titles.map((title) => (
            <li
              key={title}
              className={title === selected_title ? "flex items-baseline gap-2 text-ink" : "text-ink/40"}
            >
              {title === selected_title && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />}
              {title}
            </li>
          ))}
        </ul>
      </section>

      <article className="prose prose-lg max-w-none border-t border-ink/10 pt-10 prose-headings:font-serif prose-headings:font-medium prose-headings:text-ink prose-p:text-ink/80 prose-li:text-ink/80 prose-a:text-accent prose-strong:text-ink">
        <h1 className="!mb-8 font-serif text-3xl font-medium text-ink sm:text-4xl">{selected_title}</h1>
        <ReactMarkdown>{blog_content}</ReactMarkdown>
      </article>

      {translated_content && (
        <article className="prose prose-lg -mx-6 max-w-none border-t border-accent/30 bg-accent-soft/40 px-6 py-10 prose-headings:font-serif prose-headings:font-medium prose-headings:text-ink prose-p:text-ink/80 prose-li:text-ink/80 prose-a:text-accent prose-strong:text-ink sm:mx-0 sm:px-10">
          <p className="!mb-2 text-xs font-medium uppercase tracking-wide text-accent">
            Translation — {target_language}
          </p>
          <h1 className="!mt-0 !mb-8 font-serif text-3xl font-medium text-ink sm:text-4xl">{translated_title}</h1>
          <ReactMarkdown>{translated_content}</ReactMarkdown>
        </article>
      )}
    </div>
  );
}
