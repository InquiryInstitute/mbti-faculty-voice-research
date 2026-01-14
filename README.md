# MBTI x Faculty Voice Accuracy Research

**Investigating the Value of MBTI in Prompt Engineering for Faculty Agent Accuracy**

This repository contains experimental code and data for evaluating whether Myers-Briggs Type Indicator (MBTI) personality overlays improve voice accuracy and consistency in AI faculty agents.

## Overview

This research investigates whether MBTI provides measurable value in prompt engineering for improving the accuracy, consistency, and interpretability of faculty-style AI agents. We evaluate MBTI's utility as a scaffolding layer for role conditioning, reasoning style modulation, and epistemic posture control.

**Key Question:** Does MBTI improve faculty agent accuracy—or merely add aesthetic flavor?

## Research Design

### Experiment Structure

- **10 Faculty Personae** × **16 MBTI Types** × **3 Test Prompts** = **480 Trials**

Each trial generates:
- A faculty agent response (200-350 words)
- LLM-as-judge scores for:
  - Voice accuracy (1-5)
  - Style marker coverage (0-1)
  - Persona consistency (1-5)
  - Clarity (1-5)
  - Overfitting to MBTI (1-5)
- Rationales and textual cues from the judge

### Faculty Personae

The experiment uses 10 diverse historical figures as faculty personae:

1. **Plato** - Philosophy (dialectics, ethics, politics)
2. **Jane Austen** - Social satire, manners, moral psychology
3. **Friedrich Nietzsche** - Philosophy (genealogy, critique of morality)
4. **Jorge Luis Borges** - Literature, metaphysics, labyrinths of thought
5. **Ada Lovelace** - Computation, systems thinking, imagination in mechanism
6. **Marie Curie** - Experimental science, rigor, perseverance
7. **Charles Darwin** - Natural history, evolution, careful inference
8. **Carl Sagan** - Science communication, skepticism, wonder
9. **Sun Tzu** - Strategy, incentives, conflict minimization
10. **Mary Shelley** - Romantic literature, ethics of creation, human longing

Each persona has:
- Voice specification
- Signature moves
- Avoid patterns
- Style markers

### MBTI Types Tested

All 16 MBTI types:
- **INTJ, INTP, ENTJ, ENTP**
- **INFJ, INFP, ENFJ, ENFP**
- **ISTJ, ISFJ, ESTJ, ESFJ**
- **ISTP, ISFP, ESTP, ESFP**

## Setup

### Requirements

```bash
pip install openai pydantic python-dotenv
```

### Environment Variables

**Using OpenRouter (Recommended):**

```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Optional: Model selection (OpenRouter format)
export OPENAI_MODEL="openai/gpt-4o"
export OPENAI_JUDGE_MODEL="openai/gpt-4o"
```

**Or using direct OpenAI:**

```bash
export OPENAI_API_KEY="sk-your-key-here"

# Optional
export OPENAI_MODEL="gpt-4o"
export OPENAI_JUDGE_MODEL="gpt-4o"
```

The script automatically detects OpenRouter keys (starting with `sk-or-v1-`) and configures accordingly.

### Running the Experiment

```bash
python mbti_voice_eval.py
```

This will:
1. Generate responses for all persona/MBTI/prompt combinations
2. Evaluate each response with an LLM judge
3. Write results to:
   - `mbti_voice_results.jsonl` (full records with metadata)
   - `mbti_voice_results.csv` (tabular format for analysis)

### Quick Summary

After running, view aggregated results:

```python
from mbti_voice_eval import summarize
summarize("mbti_voice_results.csv")
```

This prints average voice accuracy by persona and by MBTI type.

## Output Format

### CSV Columns

- `persona_key`, `persona_name` - Faculty persona identifier
- `mbti` - MBTI type used
- `prompt_id`, `prompt` - Test prompt identifier and text
- `generated_text` - Faculty agent response
- `voice_accuracy` - Judge score (1-5)
- `style_marker_coverage` - Fraction of expected markers present (0-1)
- `persona_consistency` - Sustained voice score (1-5)
- `clarity` - Readability score (1-5)
- `overfitting_to_mbti` - Caricature risk (1-5, lower is better)
- `rationales` - JSON array of judge rationales
- `cues` - JSON array of textual cues cited

### JSONL Format

Each line contains a complete record with:
- All CSV fields
- Full persona specification
- Model identifiers
- Timestamp

## Research Questions

1. **Does MBTI improve voice accuracy?** Compare scores across MBTI types.
2. **Which MBTI types work best for which personae?** Identify optimal pairings.
3. **Does MBTI cause overfitting?** Monitor the `overfitting_to_mbti` score.
4. **Are some personae more sensitive to MBTI?** Analyze variance by persona.

## Related Work

This research supports the paper:

> **"Investigating the Value of MBTI in Prompt Engineering for Faculty Agent Accuracy"**  
> Daniel Du Kinque  
> Inquiry Institute, Faculty of Artificial Intelligence & Cognitive Systems

See the full paper for theoretical context, methodology, and conclusions.

## License

[Specify license - e.g., MIT, CC BY-NC 4.0, etc.]

## Citation

If you use this research, please cite:

```
Du Kinque, D. (2025). Investigating the Value of MBTI in Prompt Engineering 
for Faculty Agent Accuracy. Inquiry Institute, Faculty of Artificial 
Intelligence & Cognitive Systems.
```

## Contributing

This is a research repository. For questions or contributions, please open an issue or contact the Inquiry Institute.

## Acknowledgments

- Inquiry Institute Faculty of Artificial Intelligence
- Syzygy Cognitive Systems Lab
- Terpedia Knowledge Graph Initiative
