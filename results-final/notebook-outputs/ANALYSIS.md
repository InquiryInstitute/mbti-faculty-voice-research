# Analysis Guide

This document provides guidance for analyzing the experimental results.

## Data Files

After running the experiment, you'll have:

- `mbti_voice_results.csv` - Tabular data for statistical analysis
- `mbti_voice_results.jsonl` - Full records with metadata

## Key Metrics

### Primary Outcome: Voice Accuracy

**Question:** Does MBTI improve voice accuracy?

- Compare mean `voice_accuracy` scores across MBTI types
- Test for significant differences using ANOVA or t-tests
- Look for MBTI types that consistently score higher/lower

### Secondary Outcomes

1. **Style Marker Coverage**  
   - Fraction of expected style markers present
   - Higher = more persona-consistent

2. **Persona Consistency**  
   - Sustained voice across the response
   - Higher = less drift

3. **Clarity**  
   - Readability and structure
   - Should remain high regardless of MBTI

4. **Overfitting to MBTI**  
   - Risk of caricature
   - Lower = more natural

## Analysis Questions

### 1. Does MBTI improve voice accuracy?

```python
import pandas as pd
import scipy.stats as stats

df = pd.read_csv('mbti_voice_results.csv')
df = df[df['voice_accuracy'] >= 0]  # Remove errors

# Compare with/without MBTI (if you have control group)
# Or compare across MBTI types
mbti_groups = df.groupby('mbti')['voice_accuracy']
print(mbti_groups.mean().sort_values(ascending=False))
```

### 2. Which MBTI types work best for which personae?

```python
# Persona × MBTI interaction
pivot = df.pivot_table(
    values='voice_accuracy',
    index='persona_name',
    columns='mbti',
    aggfunc='mean'
)
print(pivot)
```

### 3. Does MBTI cause overfitting?

```python
# Lower overfitting_to_mbti is better
overfitting = df.groupby('mbti')['overfitting_to_mbti'].mean()
print(overfitting.sort_values())
```

### 4. Are some personae more sensitive to MBTI?

```python
# Variance in voice_accuracy by persona
variance_by_persona = df.groupby('persona_name')['voice_accuracy'].std()
print(variance_by_persona.sort_values(ascending=False))
```

## Visualization Ideas

1. **Heatmap:** Persona × MBTI voice accuracy scores
2. **Box plots:** Voice accuracy distribution by MBTI type
3. **Scatter plot:** Voice accuracy vs. overfitting to MBTI
4. **Bar chart:** Average scores by persona

## Statistical Tests

- **ANOVA:** Test for differences across MBTI types
- **Post-hoc tests:** Identify which MBTI types differ significantly
- **Correlation:** Voice accuracy vs. other metrics
- **Regression:** Predict voice accuracy from MBTI dimensions (I/E, S/N, T/F, J/P)

## Expected Findings

Based on the theoretical framework:

1. **Some MBTI types should improve voice accuracy** for specific personae
2. **Overfitting should be low** if MBTI is applied subtly
3. **Persona consistency should improve** with appropriate MBTI overlay
4. **Clarity should remain stable** across MBTI types

## Reporting Results

When reporting, include:

- Mean voice accuracy by MBTI type
- Optimal MBTI types per persona (if any)
- Overfitting scores (should be low)
- Statistical significance tests
- Effect sizes
- Limitations and caveats
