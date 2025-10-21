
zsh_llm_suggestions_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'

    cleanup() {
      kill $pid
      echo -ne "\e[?25h"
    }
    trap cleanup SIGINT

    echo -ne "\e[?25l"
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]" "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b"
    done
    printf "    \b\b\b\b"

    echo -ne "\e[?25h"
    trap - SIGINT
}

zsh_llm_suggestions_run_query() {
  local llm="$1"
  local query="$2"
  local result_file="$3"
  local mode="$4"

  # Try uv tool install method first (commands in PATH)
  if [[ "$llm" == *"openai"* ]] && command -v zsh-llm-openai &> /dev/null; then
    # Use installed command (uv tool install method)
    echo -n "$query" | zsh-llm-openai "$mode" > "$result_file"
  elif [[ "$llm" == *"copilot"* ]] && command -v zsh-llm-copilot &> /dev/null; then
    # Use installed command (uv tool install method)
    echo -n "$query" | zsh-llm-copilot "$mode" > "$result_file"
  else
    # Fall back to git clone method - use src/ package files
    local backend_script=""
    if [[ "$llm" == *"openai"* ]]; then
      backend_script="$SCRIPT_DIR/src/zsh_llm_suggestions/openai_backend.py"
    else
      backend_script="$SCRIPT_DIR/src/zsh_llm_suggestions/copilot_backend.py"
    fi

    local python_cmd
    if command -v uv &> /dev/null; then
      python_cmd=(uv run --project $SCRIPT_DIR python)
    else
      python_cmd=(python3)
    fi
    # Security: removed eval, use proper quoting instead
    echo -n "$query" | ${python_cmd[@]} "$backend_script" "$mode" > "$result_file"
  fi
}

zsh_llm_completion() {
  local llm="$1"
  local mode="$2"
  local query=${BUFFER}

  # Empty prompt, nothing to do
  if [[ "$query" == "" ]]; then
    return
  fi

  # If the prompt is the last suggestions, just get another suggestion for the same query
  if [[ "$mode" == "generate" ]]; then
    if [[ "$query" == "$ZSH_LLM_SUGGESTIONS_LAST_RESULT" ]]; then
      query=$ZSH_LLM_SUGGESTIONS_LAST_QUERY
    else
      ZSH_LLM_SUGGESTIONS_LAST_QUERY="$query"
    fi
  fi

  # Temporary file to store the result of the background process
  # Use mktemp for security: unpredictable path prevents symlink attacks and info disclosure
  local result_file=$(mktemp /tmp/zsh-llm-suggestions.XXXXXX)
  chmod 600 "$result_file"  # Restrictive permissions - only owner can read/write
  trap "rm -f '$result_file'" EXIT  # Ensure cleanup on function exit
  # Run the actual query in the background (since it's long-running, and so that we can show a spinner)
  read < <( zsh_llm_suggestions_run_query $llm $query $result_file $mode & echo $! )
  # Get the PID of the background process
  local pid=$REPLY
  # Call the spinner function and pass the PID
  zsh_llm_suggestions_spinner $pid

  if [[ "$mode" == "generate" ]]; then
    # Place the query in the history first
    print -s $query
    # Replace the current buffer with the result
    ZSH_LLM_SUGGESTIONS_LAST_RESULT=$(cat "$result_file")
    BUFFER="${ZSH_LLM_SUGGESTIONS_LAST_RESULT}"
    CURSOR=${#ZSH_LLM_SUGGESTIONS_LAST_RESULT}
  fi
  if [[ "$mode" == "explain" ]]; then
    # Read the explanation
    local result_content=$(cat "$result_file")

    # Use print with newline to display below the current line
    # This works in ZLE context by writing directly
    print -n '\n' >&2
    print -r "$result_content" >&2
    print -n '\n' >&2

    # Redraw the prompt
    zle reset-prompt
  fi
}

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

zsh_llm_suggestions_openai() {
  zsh_llm_completion "$SCRIPT_DIR/zsh-llm-suggestions-openai.py" "generate"
}

zsh_llm_suggestions_github_copilot() {
  zsh_llm_completion "$SCRIPT_DIR/zsh-llm-suggestions-github-copilot.py" "generate"
}

zsh_llm_suggestions_openai_explain() {
  zsh_llm_completion "$SCRIPT_DIR/zsh-llm-suggestions-openai.py" "explain"
}

zsh_llm_suggestions_github_copilot_explain() {
  zsh_llm_completion "$SCRIPT_DIR/zsh-llm-suggestions-github-copilot.py" "explain"
}

zle -N zsh_llm_suggestions_openai
zle -N zsh_llm_suggestions_openai_explain
zle -N zsh_llm_suggestions_github_copilot
zle -N zsh_llm_suggestions_github_copilot_explain
