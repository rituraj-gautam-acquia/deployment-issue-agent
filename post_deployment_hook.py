import sys
import os
import json
import litellm
from litellm import completion_cost

# 1. Load Configuration File parameters
CONFIG_PATH = "litellm_config.json"
if not os.path.exists(CONFIG_PATH):
    print(f"Error: Configuration file '{CONFIG_PATH}' not found.")
    sys.exit(1)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    try:
        config = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {CONFIG_PATH} is not a valid JSON structure.")
        sys.exit(1)

# 2. Globally Configure LiteLLM Gateway
litellm.api_base = config["LITELLM_BASE_URL"]
litellm.api_key = config["LITELLM_API_KEY"]
MODEL = config["LITELLM_MODEL"]
litellm.drop_params = True 

# 3. Financial Harness Configuration
# TOTAL_COST = 0.0
# BUDGET_CAP = 5.00  # Hard budget ceiling in USD

# def call_claude_tracked(system_prompt, user_content):
#    """Executes a request to Claude while tracking and capping token costs in real-time."""
#    global TOTAL_COST
    
#    if TOTAL_COST >= BUDGET_CAP:
#        print(f"FATAL: Financial harness triggered! Budget cap of ${BUDGET_CAP:.2f} reached. Aborting processing.")
#        sys.exit(1)
        
#    response = litellm.completion(
#        model=MODEL,
#        messages=[
#            {"role": "system", "content": system_prompt},
#            {"role": "user", "content": user_content}
#        ]
#    )
    
#    call_cost = completion_cost(response)
#    TOTAL_COST += call_cost
#    print(f"   [Cost Tracker] Call Cost: ${call_cost:.5f} | Cumulative Spend: ${TOTAL_COST:.5f}")
    
#    if TOTAL_COST >= BUDGET_CAP:
#        print(f"WARNING: Cost harness breached mid-turn. Enforcing termination protocols.")
        
#    return response.choices[0].message.content

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_deploy_hook.py <path_to_log_file>")
        sys.exit(1)
        
    log_file = sys.argv[1]
    log_content = read_file(log_file)
    
    # --- STEP 1: LOG ANALYSIS ---
    print("-> Step 1: Running Drupal & Acquia Combined Log Analyzer Agent...")
    prompt_analyzer = read_file("prompts/log_analyzer.md")
    errors_extracted = call_claude_tracked(prompt_analyzer, f"Analyze this combined log stream:\n\n{log_content}")
    
    # Early Exit Check for successful builds
    clean_analysis = errors_extracted.strip().lower()
    no_error_phrases = ["no errors", "no issues", "successful", "passed", "no error found"]
    if not clean_analysis or any(phrase in clean_analysis for phrase in no_error_phrases):
        print("exited, no errors found")
        sys.exit(0)
        
    # --- STEP 2: INITIAL BRAINSTORMING ---
    print("-> Step 2: Running Issue Investigator Agent...")
    prompt_investigator = read_file("prompts/issue_investigator.md")
    current_best_solution = call_claude_tracked(prompt_investigator, f"Extracted Errors:\n{errors_extracted}")
    
    # --- STEP 3: OPTIMIZATION LOOP ---
    print("-> Step 3: Entering Solution Optimization Loop...")
    prompt_evaluator = read_file("prompts/solution_evaluator.md")
    
    MAX_LOOP_TURNS = 3  
    for turn in range(1, MAX_LOOP_TURNS + 1):
        print(f"   Running Loop Refinement Turn {turn}/{MAX_LOOP_TURNS}...")
        
        if TOTAL_COST >= BUDGET_CAP:
            print("   [Harness Notice] Breaking loop execution early due to cost limits.")
            break
            
        loop_context = (
            f"Original Combined Errors:\n{errors_extracted}\n\n"
            f"Current Proposed Remediation:\n{current_best_solution}"
        )
        
        evaluation_output = call_claude_tracked(prompt_evaluator, loop_context)
        
        if "SOLUTION_OPTIMAL" in evaluation_output:
            print("   [Loop Terminated]: Optimal solution variant identified programmatically.")
            current_best_solution = evaluation_output.replace("SOLUTION_OPTIMAL", "").strip()
            break
            
        current_best_solution = evaluation_output

    # --- STEP 4: GENERATE PAYLOAD ---
    print("-> Step 4: Formatting Final Payload via Solution Specialist Agent...")
    prompt_specialist = read_file("prompts/solution_specialist.md")
    specialist_input = f"Original Errors:\n{errors_extracted}\n\nFinalized Solution Guide:\n{current_best_solution}"
    final_payload = call_claude_tracked(prompt_specialist, specialist_input)
    
    output_filename = "coding_agent_prompt.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_payload)
        
    print(f"-> Success: Actionable Drupal instructions compiled in {output_filename}")
    print(f"-> Final Run Cost: ${TOTAL_COST:.4f}")

if __name__ == "__main__":
    main()
