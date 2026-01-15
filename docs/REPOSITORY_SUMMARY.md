# Repository Summary

## MBTI Faculty Voice Research

This repository contains experimental code and documentation for investigating whether MBTI personality overlays improve voice accuracy in AI faculty agents.

## Repository Structure

```
mbti-faculty-voice-research/
├── README.md                 # Main documentation and overview
├── RESEARCH_PAPER.md         # Full research paper text
├── SETUP.md                  # Installation and setup guide
├── ANALYSIS.md               # Analysis methodology and guidance
├── CONTRIBUTING.md           # Contribution guidelines
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── env.example               # Environment variable template
├── .gitignore                # Git ignore patterns
├── mbti_voice_eval.py        # Main experiment script
└── [results/]                # Generated after running (gitignored)
    ├── mbti_voice_results.csv
    └── mbti_voice_results.jsonl
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run experiment:**
   ```bash
   python mbti_voice_eval.py
   ```

4. **Analyze results:**
   See `ANALYSIS.md` for guidance

## Experiment Design

- **10 Faculty Personae** (Plato, Austen, Nietzsche, Borges, Lovelace, Curie, Darwin, Sagan, Sun Tzu, Shelley)
- **16 MBTI Types** (all combinations)
- **3 Test Prompts** (domain-neutral, voice-revealing)
- **480 Total Trials**

Each trial generates:
- Faculty agent response (200-350 words)
- LLM-as-judge evaluation scores
- Rationales and textual cues

## Key Files

- **`mbti_voice_eval.py`** - Main experiment script with persona definitions and evaluation logic
- **`README.md`** - Comprehensive documentation
- **`RESEARCH_PAPER.md`** - Full academic paper text
- **`ANALYSIS.md`** - Statistical analysis guidance
- **`SETUP.md`** - Detailed setup instructions

## Research Questions

1. Does MBTI improve voice accuracy?
2. Which MBTI types work best for which personae?
3. Does MBTI cause overfitting/caricature?
4. Are some personae more sensitive to MBTI?

## Output

Results are saved in two formats:
- **CSV** (`mbti_voice_results.csv`) - Tabular format for statistical analysis
- **JSONL** (`mbti_voice_results.jsonl`) - Full records with metadata

## Next Steps

1. Run the experiment (requires OpenAI API access)
2. Analyze results using guidance in `ANALYSIS.md`
3. Compare findings with theoretical framework in `RESEARCH_PAPER.md`
4. Contribute improvements or additional personae

## License

MIT License - See LICENSE file for details

## Contact

Inquiry Institute  
Faculty of Artificial Intelligence & Cognitive Systems
