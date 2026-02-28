/**
 * SimpleMarkdown
 * A lightweight markdown-to-JSX renderer covering the subset Claude uses in briefs:
 * ## / ### headings, **bold**, *italic*, `code`, - bullet lists, 1. ordered lists,
 * blank-line paragraph breaks, and horizontal rules (---).
 *
 * Content comes from our own API so dangerouslySetInnerHTML is acceptable here.
 */

function renderInline(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-slate-800">$1</strong>')
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em class="italic">$1</em>')
    .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-slate-700 px-1 rounded text-[11px] font-mono">$1</code>')
}

interface Props {
  content: string
  className?: string
}

export function SimpleMarkdown({ content, className = '' }: Props) {
  const lines = content.split('\n')
  const blocks: React.ReactNode[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // H2
    if (line.startsWith('## ')) {
      blocks.push(
        <h2
          key={i}
          className="text-sm font-bold text-slate-800 mt-5 mb-2 pb-1 border-b border-slate-200 first:mt-0"
        >
          {line.slice(3)}
        </h2>,
      )
      i++
      continue
    }

    // H3
    if (line.startsWith('### ')) {
      blocks.push(
        <h3 key={i} className="text-xs font-semibold text-slate-700 mt-3 mb-1">
          {line.slice(4)}
        </h3>,
      )
      i++
      continue
    }

    // Horizontal rule
    if (/^---+$/.test(line.trim())) {
      blocks.push(<hr key={i} className="my-3 border-slate-200" />)
      i++
      continue
    }

    // Unordered list — collect consecutive bullet lines
    if (line.startsWith('- ') || line.startsWith('* ')) {
      const items: string[] = []
      while (i < lines.length && (lines[i].startsWith('- ') || lines[i].startsWith('* '))) {
        items.push(lines[i].slice(2))
        i++
      }
      blocks.push(
        <ul key={`ul-${i}`} className="list-disc pl-4 space-y-1 my-2">
          {items.map((item, j) => (
            <li
              key={j}
              className="text-xs text-slate-600 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: renderInline(item) }}
            />
          ))}
        </ul>,
      )
      continue
    }

    // Ordered list — collect consecutive numbered lines
    if (/^\d+\. /.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s+/, ''))
        i++
      }
      blocks.push(
        <ol key={`ol-${i}`} className="list-decimal pl-4 space-y-1 my-2">
          {items.map((item, j) => (
            <li
              key={j}
              className="text-xs text-slate-600 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: renderInline(item) }}
            />
          ))}
        </ol>,
      )
      continue
    }

    // Blank line — skip (natural spacing from surrounding elements)
    if (line.trim() === '') {
      i++
      continue
    }

    // Paragraph
    blocks.push(
      <p
        key={i}
        className="text-xs text-slate-600 leading-relaxed my-1"
        dangerouslySetInnerHTML={{ __html: renderInline(line) }}
      />,
    )
    i++
  }

  return <div className={`space-y-0.5 ${className}`}>{blocks}</div>
}
