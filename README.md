# deployment-issue-resolver

🤖 Workflow Architecture
 * Log Analysis: The Log Analyzer Agent handles multi-source evaluation, connecting deployment errors (e.g., failed drush cim) directly with the underlying server tracebacks (e.g., PHP Fatals). If the log is clean, it triggers an early exit routine printing exited, no errors found.
 * Initial Investigation: The Issue Investigator Agent uses Claude's pre-trained intelligence of Drupal core, contrib extensions, entity APIs, and Symfony service containers to deduce a baseline mitigation path.
 * Critique-and-Refine Loop: The Solution Evaluator Agent acts as a critic. It reviews the candidate solution against specific Drupal runtime implications (database updates, config schema syncs, routing cache clears) and iteratively updates the plan for up to 3 turns or until it declares SOLUTION_OPTIMAL.
 * Structured Packaging: The Solution Specialist Agent translates the finalized remediation guide into a strict, machine-readable JSON payload (coding_agent_prompt.json).
 * Financial Harness Control: Every token consumed is tracked in real-time via litellm.completion_cost(). If cumulative processing costs hit the built-in safety limit of $5.00 USD, the harness forces an immediate safe shutdown to protect against cost overruns.

## 🛑 Manual Steps & Operational Lifecycle

This repository acts as an on-demand post-deployment log analysis utility. Staging deployments, UAT windows, and Production deployments are treated as completely independent events. 

### 1. Day-to-Day Operational Workflow (The RE Runbook)
Because deployments are handled manually by the Release Engineer (RE) on independent timelines, follow these steps to trigger the analysis:
## Phase 1: Staging Analysis
1. The RE manually executes the deployment to the Acquia Staging environment.
2. Once complete, the RE opens the GitLab pipeline for the target branch.
3. Click the Play (▶️) button on the ⁠analyze_stage_deployment⁠ job.
4. The agent will pull the staging logs, run the optimization loop, and output errors if found.
## Phase 2: The UAT Gap (Typically 5 Days)
 The repository remains completely idle. No automatic jobs will trigger or push configurations to production during this validation period.

### 2. Initial One-Time Repository Setup
Ensure your local environment secrets do not get committed to the repository history by adding these files to your `.gitignore`:
litellm_config.json
combined_deployment.log
acquia_*.log
 * Configure Git Exclusions: Ensure that litellm_config.json is explicitly declared inside your repository’s .gitignore file so that developer API tokens are never accidentally committed.
   # .gitignore snippet text 
   
### 3. Configure GitLab CI/CD Variables (Cloud Setup)
Navigate to your GitLab Project ➔ Settings ➔ CI/CD ➔ Variables, and manually populate the required runtime keys.
Check Mask variable for all keys so they never leak in raw execution logs. Check Protect variable for production keys to restrict them to verified branches.
| Variable Key | Scope / Target | Security | Description |
|---|---|---|---|
| STAGE_LITELLM_BASE_URL | Staging Environment | Cleartext | Endpoint URL for the LiteLLM proxy gateway |
| STAGE_LITELLM_API_KEY | Staging Environment | Masked | Your custom LiteLLM proxy access token |
| STAGE_LITELLM_MODEL | Staging Environment | Cleartext | Model alias (e.g., openai/claude-3-5-sonnet) |
| ACQUIA_STAGE_API_KEY | Staging Environment | Masked | Acquia Cloud Platform API access key |
| ACQUIA_STAGE_API_SECRET | Staging Environment | Masked | Acquia Cloud Platform API access secret |
| ACQUIA_STAGE_ENV_UUID | Staging Environment | Cleartext | Target Acquia Staging Environment Application UUID |
| PROD_LITELLM_BASE_URL | Production Environment | Cleartext | Endpoint URL for the Production LiteLLM proxy gateway |
| PROD_LITELLM_API_KEY | Production Environment | Masked & Protected | Your Production LiteLLM proxy access token |
| PROD_LITELLM_MODEL | Production Environment | Cleartext | Production model identifier mapping |
| ACQUIA_PROD_API_KEY | Production Environment | Masked & Protected | Acquia Production API access key |
| ACQUIA_PROD_API_SECRET | Production Environment | Masked & Protected | Acquia Production API access secret |
| ACQUIA_PROD_ENV_UUID | Production Environment | Cleartext | Target Acquia Production Environment Application UUID |


## Phase 3: Production Analysis
1. After UAT approval, the RE manually executes the deployment to the live Acquia Production environment.
2. Once complete, the RE opens the GitLab pipeline.
3. Click the Play (▶️) button on the ⁠analyze_prod_deployment⁠ job.
4. The agent will target your live production logs, scrape for anomalies (PHP errors, Watchdog drops, Apache issues), and generate a ⁠coding_agent_prompt.json⁠ artifact only if a post-launch failure is detected.
