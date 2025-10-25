# OPS Strategic Director - LLM Integration

## Overview

The OPS Strategic Director now supports LLM-powered strategic intelligence, enabling true AI-driven decision-making for
cryptanalysis operations. The system gracefully falls back to rule-based logic when LLM is unavailable.

## Features

### Supported LLM Providers

- **OpenAI** (GPT-4, GPT-3.5-turbo, etc.)
- **Anthropic** (Claude-3 Opus, Sonnet, etc.)
- **Local** (Rule-based fallback - no API required)

### Key Capabilities

1. **Intelligent Strategic Analysis**: LLM analyzes attack progress, agent insights, and historical context to make
informed decisions 2. **Graceful Degradation**: Automatically falls back to rule-based logic if LLM unavailable or fails
3. **Structured Decisions**: LLM outputs JSON-formatted decisions with reasoning, confidence scores, and success
criteria 4. **Cost Awareness**: Configurable cost limits to prevent runaway API expenses 5. **Decision Caching**: Avoids
re-analyzing identical situations (1-hour TTL)

## Configuration

### Environment Setup

Set your API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY=sk-your-key-here

# For Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Config File

Edit `config/llm_config.yaml`:

```yaml
# Provider: openai, anthropic, or local (rule-based)
provider: openai

# Model configuration
openai:
  model: gpt-4
  temperature: 0.7
  max_tokens: 1000

anthropic:
  model: claude-3-5-sonnet-20241022
  temperature: 0.7
  max_tokens: 1000

# Cost management
cost_limits:
  max_daily_spend: 50.0
  warn_threshold: 40.0
```

## Usage

### Command Line

```bash
# Use OpenAI GPT-4 for strategic decisions
kryptos autonomous --llm-provider openai --llm-model gpt-4

# Use Anthropic Claude
kryptos autonomous --llm-provider anthropic --llm-model claude-3-5-sonnet-20241022

# Use rule-based fallback (no LLM)
kryptos autonomous --llm-provider local
```

### Python API

```python
from kryptos.agents.ops_director import OpsStrategicDirector, AgentInsight, AttackProgress
from datetime import datetime

# Initialize with OpenAI
ops = OpsStrategicDirector(
    llm_provider="openai",
    model="gpt-4",
    cache_dir="./data/ops_strategy"
)

# Update attack progress
ops.update_attack_progress(
    attack_type="hill_3x3",
    attempts=1_000_000,
    best_score=0.25
)

# Register agent insights
ops.register_agent_insight(
    AgentInsight(
        agent_name="SPY",
        timestamp=datetime.now(),
        category="linguistic",
        description="Found strong rhyme pattern in candidate #1247",
        confidence=0.85,
        actionable=True,
        metadata={"candidate_id": 1247}
    )
)

# Get strategic decision
decision = ops.analyze_situation(force_decision=True)

print(f"Action: {decision.action}")
print(f"Reasoning: {decision.reasoning}")
print(f"Confidence: {decision.confidence}")
```

## LLM Decision Process

### 1. Situation Analysis

OPS gathers comprehensive context:
- Active attack progress (attempts, scores, improvement rates)
- Recent agent insights (SPY, K123 Analyzer, Web Intel)
- Decision history (what worked, what didn't)

### 2. Prompt Construction

Builds a detailed prompt including:
- Current attack status
- Hours since last improvement
- Agent discoveries and patterns
- Available strategic actions (CONTINUE, PIVOT, BOOST, etc.)
- JSON response format

### 3. LLM Processing

Sends prompt to LLM and receives structured JSON response:

```json
{
  "action": "PIVOT",
  "reasoning": "Hill climbing stagnant for 9 hours with no improvement. SPY found linguistic patterns suggesting Vigenere structure. Recommend pivoting to period-14 Vigenere attack.",
  "affected_attacks": ["hill_3x3"],
  "resource_changes": {"hill_3x3": 0.0, "vigenere_period_14": 0.7},
  "success_criteria": "New attack should improve score >0.30 within 4 hours",
  "review_in_hours": 4.0,
  "confidence": 0.85
}
```

### 4. Decision Execution

OPS executes the decision:
- Adjusts resource allocation
- Starts/stops attacks
- Updates coordination state
- Logs decision for future learning

### 5. Fallback to Rules

If LLM fails or unavailable:
- Uses rule-based logic
- Simple heuristics (e.g., pivot if stagnant >8 hours)
- Lower confidence scores
- Still produces valid decisions

## Strategic Actions

### CONTINUE
Keep current approach running (steady progress)

### BOOST
Increase CPU/resources to current approach (showing promise)

### REDUCE
Decrease resources (diminishing returns)

### PIVOT
Switch to different attack approach (stagnant)

### STOP
Abandon approach entirely (no progress)

### START_NEW
Begin new attack type (insights suggest new direction)

### EMERGENCY_STOP
Human intervention needed (system issue)

## Cost Management

### Typical Costs (as of 2024)

**OpenAI GPT-4:**
- Input: ~$10/1M tokens
- Output: ~$30/1M tokens
- ~1,000 tokens per decision
- Estimated cost: ~$0.02-0.04 per decision

**Anthropic Claude-3:**
- Input: ~$3/1M tokens
- Output: ~$15/1M tokens
- ~1,000 tokens per decision
- Estimated cost: ~$0.01-0.02 per decision

### Budget Example

With 30-second OPS cycles (120 decisions/hour):
- 24-hour operation: ~2,880 decisions
- At $0.03/decision: **$86.40/day**
- At $0.01/decision: **$28.80/day**

**Recommendation:** Start with hourly OPS cycles (24 decisions/day) for testing, then optimize frequency based on
results.

## Testing

### Run Tests

```bash
# All OPS LLM tests
pytest tests/test_ops_llm_integration.py -v

# Specific test categories
pytest tests/test_ops_llm_integration.py::TestRuleBasedDecisions -v
pytest tests/test_ops_llm_integration.py::TestLLMResponseParsing -v
pytest tests/test_ops_llm_integration.py::TestLLMIntegration -v
```

### Test Coverage

- LLM client initialization (OpenAI, Anthropic, local)
- Rule-based fallback decisions
- Prompt construction and context inclusion
- JSON response parsing (valid/invalid)
- Full integration flow with mocked LLM
- Decision persistence

All 16 tests passing in <2 seconds.

## Best Practices

### 1. Start with Rule-Based

```bash
# Test autonomous system with rule-based logic first
kryptos autonomous --llm-provider local --cycle-interval 0.25
```

Verify system works before adding LLM costs.

### 2. Test with Short Runs

```bash
# 10-minute test run with OpenAI
kryptos autonomous --llm-provider openai --max-cycles 20
```

Monitor costs and decision quality.

### 3. Use Longer OPS Cycles

```bash
# Check OPS every 30 minutes instead of 30 seconds
kryptos autonomous --ops-cycle 30
```

Reduces API calls while still providing strategic guidance.

### 4. Monitor Decision Quality

```bash
# Review decision history
cat data/ops_strategy/decisions.jsonl | jq .

# Check recent decisions
tail -5 data/ops_strategy/decisions.jsonl | jq .
```

### 5. Set Cost Limits

Edit `config/llm_config.yaml`:

```yaml
cost_limits:
  max_daily_spend: 10.0  # Stop at $10/day
  warn_threshold: 8.0    # Warn at $8/day
```

## Troubleshooting

### "Warning: OPENAI_API_KEY not set"

Set your API key:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "Warning: openai package not installed"

Install dependencies:
```bash
pip install openai>=1.0.0
```

### "Warning: LLM call failed"

Check:
- API key is valid
- Internet connection working
- API rate limits not exceeded
- Model name is correct

System will automatically fall back to rule-based logic.

### High API Costs

Reduce frequency:
- Increase `--ops-cycle` (e.g., from 0.5 to 60 minutes)
- Use cheaper model (GPT-3.5-turbo instead of GPT-4)
- Switch to Anthropic Claude (generally cheaper)

## Examples

### Example 1: Detecting Stagnation

**Situation:**
- Hill climbing at 1M attempts, score 0.15
- No improvement for 9 hours

**LLM Decision:**
```json
{
  "action": "PIVOT",
  "reasoning": "Hill climbing exhausted search space with no improvement for 9 hours. Agent insights suggest trying different cipher family.",
  "affected_attacks": ["hill_3x3"],
  "resource_changes": {"hill_3x3": 0.0, "vigenere_period_14": 0.6},
  "success_criteria": "New attack improves score >0.20 within 4 hours",
  "review_in_hours": 4.0,
  "confidence": 0.85
}
```

### Example 2: Boosting Promising Attack

**Situation:**
- Vigenere attack showing rapid improvement
- SPY detected coherent linguistic patterns

**LLM Decision:**
```json
{
  "action": "BOOST",
  "reasoning": "Vigenere period-14 showing strong improvement trend (0.20→0.35 in 2 hours). SPY confirms linguistic coherence. Increase resources to accelerate.",
  "affected_attacks": ["vigenere_period_14"],
  "resource_changes": {"vigenere_period_14": 0.9},
  "success_criteria": "Continue improvement at >0.05/hour",
  "review_in_hours": 1.0,
  "confidence": 0.92
}
```

### Example 3: Starting New Attack

**Situation:**
- Web intel found new crib: "BERLINCLOCK"
- No active crib-guided attacks

**LLM Decision:**
```json
{
  "action": "START_NEW",
  "reasoning": "Web intelligence discovered high-confidence crib 'BERLINCLOCK'. Start crib-guided attack to exploit this finding.",
  "affected_attacks": [],
  "resource_changes": {"crib_guided_berlinclock": 0.5},
  "success_criteria": "Find valid plaintext containing crib within 8 hours",
  "review_in_hours": 8.0,
  "confidence": 0.78
}
```

## Future Enhancements

### Planned Features

1. **Multi-Agent LLM Coordination**: Different LLMs for different roles (strategist, analyst, critic) 2. **Fine-Tuned
Models**: Train on cryptanalysis-specific data 3. **Cost Optimization**: Batch decisions, use cheaper models for routine
decisions 4. **Learning from Success**: Update strategy KB with successful decision patterns 5. **Human-in-the-Loop**:
Request human approval for high-risk decisions 6. **Adversarial Validation**: Second LLM critiques first LLM's decisions

### Research Questions

- Can LLM identify novel attack strategies from literature?
- Does Claude vs GPT-4 produce different strategic insights?
- What's the optimal OPS cycle frequency for cost vs. quality?
- Can LLM learn from past decision outcomes to improve?

## Related Documentation

- [Autonomous System Architecture](AUTONOMOUS_SYSTEM.md)
- [OPS Strategic Framework](../src/kryptos/agents/ops_director.py)
- [Agent Insights](../src/kryptos/agents/)
- [Decision History](../data/ops_strategy/decisions.jsonl)
