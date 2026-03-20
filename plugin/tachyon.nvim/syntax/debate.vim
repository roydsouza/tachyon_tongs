" Tachyon Tongs: Debate Transcript Syntax Highlighting
if exists("b:current_syntax")
  finish
endif

syntax match debateAnalyst "\[Analyst\]"
syntax match debateSkeptic "\[Skeptic\]"
syntax match debateVerdict "\[Verdict\]"
syntax region debateQuote start="\"" end="\"" skip="\\\""

highlight link debateAnalyst Keyword
highlight link debateSkeptic Special
highlight link debateVerdict Statement
highlight link debateQuote String

let b:current_syntax = "debate"
