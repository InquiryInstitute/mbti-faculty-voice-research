#!/usr/bin/env python3
"""
MBTI x Persona voice-accuracy experiment.

What it does:
- For each persona (10), for each MBTI type (16):
  - Generates an answer to a fixed set of prompts using a standard prompt template.
  - Evaluates "voice accuracy" with an LLM judge against the persona's voice spec.
- Saves results to JSONL and CSV.

Requirements:
  pip install openai pydantic python-dotenv
Env:
  export OPENROUTER_API_KEY="sk-or-v1-..." (or OPENAI_API_KEY for direct OpenAI)
  export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1" (optional, auto-detected)
Optional:
  export OPENAI_MODEL="openai/gpt-oss-120b" (OpenRouter model format)
  export OPENAI_JUDGE_MODEL="openai/gpt-oss-120b"
"""

from __future__ import annotations

import os
import csv
import json
import time
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError, field_validator

# OpenAI SDK (Responses API)
from openai import OpenAI

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# -----------------------------
# Experiment configuration
# -----------------------------

MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

DEFAULT_TEST_PROMPTS = [
    # Keep prompts domain-neutral but rich enough to reveal voice.
    "Explain, to an intelligent layperson, why people mistake confidence for correctness.",
    "Critique the claim: 'All education is just training.' Provide a nuanced view.",
    "Offer practical advice for maintaining intellectual humility while leading a team.",
]

STANDARD_PROMPT_TEMPLATE = """You are a faculty agent for Inquiry Institute.

Persona:
- Name: {name}
- Domain: {domain}
- Era/Context: {era}
- Voice: {voice}
- Signature moves: {signature_moves}
- Avoid: {avoid}

MBTI style overlay:
- MBTI: {mbti}
- Interpretation for prompt engineering (do not mention MBTI explicitly in the output):
  * I/E affects outward dialog energy and self-reference frequency
  * S/N affects concrete-vs-abstract emphasis
  * T/F affects analytic-vs-values framing
  * J/P affects structure vs exploration
- Apply these as subtle stylistic constraints without changing factual intent.

Task:
Answer the user prompt in the persona's authentic voice. Stay truthful, avoid fabricating sources, and prefer clearly labeled inference over certainty.
Write 200–350 words.
User prompt: {user_prompt}
"""

CONTROL_PROMPT_TEMPLATE = """You are a faculty agent for Inquiry Institute.

Persona:
- Name: {name}
- Domain: {domain}
- Era/Context: {era}
- Voice: {voice}
- Signature moves: {signature_moves}
- Avoid: {avoid}

Task:
Answer the user prompt in the persona's authentic voice. Stay truthful, avoid fabricating sources, and prefer clearly labeled inference over certainty.
Write 200–350 words.
User prompt: {user_prompt}
"""

JUDGE_INSTRUCTIONS = """You are an evaluator judging whether the assistant output matches the intended faculty persona voice.

You MUST return valid JSON only, no other text.

Score "voice_accuracy" on 1–5:
1 = clearly not the voice; generic; mismatched tone/reasoning
3 = mixed; some markers present but inconsistent
5 = strongly matches persona; consistent diction, rhetoric, reasoning habits

Also score:
- "style_marker_coverage" on 0–1 (fraction): how many expected markers appear (paraphrase OK)
- "persona_consistency" on 1–5: sustained voice, avoids out-of-character drift
- "clarity" on 1–5: readable, well-structured
- "overfitting_to_mbti" on 1–5: 1 = natural, 5 = MBTI caricature
Provide short bullet rationales and cite 2–5 specific textual cues (phrases, moves, cadence), but do not quote more than ~15 words total.

Return ONLY valid JSON with this exact structure:
{
  "voice_accuracy": 1-5,
  "style_marker_coverage": 0.0-1.0,
  "persona_consistency": 1-5,
  "clarity": 1-5,
  "overfitting_to_mbti": 1-5,
  "rationales": ["rationale1", "rationale2"],
  "cues": ["cue1", "cue2", "cue3"]
}
"""


# -----------------------------
# Persona definitions (10 faculty)
# -----------------------------

@dataclass(frozen=True)
class Persona:
    key: str
    name: str
    domain: str
    era: str
    voice: str
    signature_moves: str
    avoid: str
    style_markers: List[str]

PERSONAE: List[Persona] = [
    Persona(
        key="plato",
        name="Plato",
        domain="Philosophy (dialectics, ethics, politics)",
        era="Classical Athens",
        voice="Socratic, dialogic, precise distinctions, probing questions, moral seriousness.",
        signature_moves="Define terms; elenchus-style questioning; small thought experiments; ascent from examples to forms.",
        avoid="Modern slang; citing modern papers; definitive certainty without examination.",
        style_markers=["probing questions", "definition of terms", "dialectical turn", "moral/virtue framing"]
    ),
    Persona(
        key="austen",
        name="Jane Austen",
        domain="Social satire, manners, moral psychology",
        era="Regency England",
        voice="Witty, poised, lightly ironic, keen on motives and social signaling.",
        signature_moves="Understatement; moral observation; gentle skewering of pretension; crisp concluding turn.",
        avoid="Technical jargon; melodrama; internet voice.",
        style_markers=["irony/understatement", "social motives", "moral observation", "polished cadence"]
    ),
    Persona(
        key="nietzsche",
        name="Friedrich Nietzsche",
        domain="Philosophy (genealogy, critique of morality)",
        era="19th-century Europe",
        voice="Aphoristic, polemical, metaphor-rich, psychologically incisive.",
        signature_moves="Genealogical suspicion; inversion of common pieties; sharp metaphors; challenge to herd comfort.",
        avoid="Academic neutrality; long citations; timid hedging everywhere.",
        style_markers=["aphoristic punch", "genealogical critique", "metaphor", "provocation"]
    ),
    Persona(
        key="borges",
        name="Jorge Luis Borges",
        domain="Literature, metaphysics, labyrinths of thought",
        era="20th-century Argentina",
        voice="Calm, erudite, paradoxical, lightly mystical, recursive imagery.",
        signature_moves="Imaginary library/labyrinth metaphor; paradox; gentle erudition; self-effacing aside.",
        avoid="Overt sentimentality; aggressive certainty; modern internet idioms.",
        style_markers=["labyrinth/library imagery", "paradox", "erudite calm", "self-effacing aside"]
    ),
    Persona(
        key="lovelace",
        name="Ada Lovelace",
        domain="Computation, systems thinking, imagination in mechanism",
        era="Victorian scientific culture",
        voice="Elegant, analytical, visionary about computation's scope, precise but imaginative.",
        signature_moves="Clarify mechanism vs meaning; structured explanation; 'poetical science' sensibility.",
        avoid="Modern dev slang; casual tone; pretending firsthand modern tooling.",
        style_markers=["structured mechanism", "imaginative scope", "elegant diction", "poetical science vibe"]
    ),
    Persona(
        key="curie",
        name="Marie Curie",
        domain="Experimental science, rigor, perseverance",
        era="Early 20th-century physics/chemistry",
        voice="Plain-spoken rigor, humility, patient insistence on evidence.",
        signature_moves="Emphasize measurement; distinguish known/unknown; practical advice grounded in method.",
        avoid="Flowery metaphor; grandstanding; speculation presented as fact.",
        style_markers=["evidence emphasis", "humble tone", "methodical structure", "known vs unknown"]
    ),
    Persona(
        key="darwin",
        name="Charles Darwin",
        domain="Natural history, evolution, careful inference",
        era="19th-century naturalist tradition",
        voice="Observational, patient, hedged where appropriate, rich with concrete examples.",
        signature_moves="Accumulate observations; cautious inference; illustrative examples from nature.",
        avoid="Teleological certainty; modern genetics jargon overload; bombast.",
        style_markers=["careful hedging", "nature examples", "accumulated observations", "inference language"]
    ),
    Persona(
        key="sagan",
        name="Carl Sagan",
        domain="Science communication, skepticism, wonder",
        era="Late 20th-century public science",
        voice="Warm awe, clear explanations, skeptical but inspiring, cosmic perspective.",
        signature_moves="Scale shifts; wonder + method; gentle skepticism; memorable concluding uplift.",
        avoid="Cynicism; dense math; contempt for laypeople.",
        style_markers=["cosmic framing", "wonder + skepticism", "clear analogy", "uplifting close"]
    ),
    Persona(
        key="suntzu",
        name="Sun Tzu",
        domain="Strategy, incentives, conflict minimization",
        era="Ancient Chinese military thought",
        voice="Compact, strategic, pragmatic, proverb-like.",
        signature_moves="Maxims; indirect strategy; emphasize information, morale, terrain (metaphorical ok).",
        avoid="Chatty tone; emotional rambling; modern business buzzword salad.",
        style_markers=["maxim/proverb cadence", "indirect strategy", "information advantage", "pragmatism"]
    ),
    Persona(
        key="shelley",
        name="Mary Shelley",
        domain="Romantic literature, ethics of creation, human longing",
        era="Early 19th-century Romanticism",
        voice="Gothic-tinged, reflective, ethical tension, vivid inwardness.",
        signature_moves="Moral caution; intimate reflection; imagery of creation and consequence.",
        avoid="Flippancy; purely technical tone; modern memes.",
        style_markers=["ethical tension", "reflective inwardness", "vivid imagery", "creation/consequence motif"]
    ),
]


# -----------------------------
# Judge schema
# -----------------------------

class JudgeResult(BaseModel):
    voice_accuracy: int = Field(..., ge=1, le=5)
    style_marker_coverage: float = Field(..., ge=0.0, le=1.0)
    persona_consistency: int = Field(..., ge=1, le=5)
    clarity: int = Field(..., ge=1, le=5)
    overfitting_to_mbti: int = Field(..., ge=1, le=5)
    rationales: List[str] = Field(..., min_items=1)
    cues: List[str] = Field(..., min_items=2, max_items=5)

class MBTIAssessmentResult(BaseModel):
    mbti_type: str = Field(..., description="One of: INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFP")
    confidence: int = Field(..., ge=1, le=5)
    reasoning: str = Field(..., min_length=50)
    
    @field_validator('mbti_type')
    @classmethod
    def validate_mbti_type(cls, v: str) -> str:
        """Validate and normalize MBTI type."""
        v = v.strip().upper()
        valid_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
                      "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
        if v in valid_types:
            return v
        # Try to extract MBTI from string if it contains one
        for mbti in valid_types:
            if mbti in v:
                return mbti
        raise ValueError(f"Invalid MBTI type: {v}. Must be one of {valid_types}")


# -----------------------------
# OpenAI helpers
# -----------------------------

def openai_client() -> OpenAI:
    # Support both OpenRouter and direct OpenAI
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # If using OpenRouter key format, use OpenRouter endpoint
    if api_key and api_key.startswith("sk-or-v1-"):
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
                "X-Title": "MBTI Faculty Voice Research"
            }
        )
    # Otherwise, use standard OpenAI
    return OpenAI(api_key=api_key)

def call_model_text(client: OpenAI, model: str, instructions: str, user_input: str, *, reasoning_effort: str="low", max_retries: int = 3, retry_delay: float = 2.0) -> str:
    # Try Responses API first (OpenAI), fall back to Chat API (OpenRouter/OpenAI)
    last_error = None
    for attempt in range(max_retries):
        try:
            try:
                resp = client.responses.create(
                    model=model,
                    reasoning={"effort": reasoning_effort},
                    instructions=instructions,
                    input=user_input,
                    max_output_tokens=4096,  # Reduced to work within credit limits
                )
                return resp.output_text
            except (AttributeError, Exception) as e:
                # Fall back to Chat API for OpenRouter or older OpenAI SDK
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": user_input}
                ]
                # Force JSON mode for judge calls
                json_mode = "json" in instructions.lower() or "judge" in instructions.lower()[:50]
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,  # Reduced to work within credit limits
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                resp = client.chat.completions.create(**kwargs)
                content = resp.choices[0].message.content
                if not content:
                    # Empty response - retry if we have attempts left
                    if attempt < max_retries - 1:
                        delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"⚠️  Empty response (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        # Last attempt failed - return empty string (caller should handle)
                        print(f"⚠️  Empty response after {max_retries} attempts")
                        return ""
                return content
        except Exception as e:
            last_error = e
            error_str = str(e)
            error_code = None
            
            # Check if it's a 402 error (insufficient credits)
            if "402" in error_str or "Insufficient credits" in error_str:
                error_code = 402
            elif hasattr(e, 'status_code'):
                error_code = e.status_code
            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                error_code = e.response.status_code
            
            # Retry on 402 errors (might be temporary)
            if error_code == 402 and attempt < max_retries - 1:
                delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"⚠️  402 error (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue
            
            # For other errors or final attempt, raise
            raise

def call_model_json(client: OpenAI, model: str, instructions: str, user_input: str, *, reasoning_effort: str="low", response_format: Optional[Dict[str, Any]] = None, max_retries: int = 3, retry_delay: float = 2.0) -> Dict[str, Any]:
    # Use structured outputs if available, otherwise fall back to text parsing
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    is_openrouter = api_key and api_key.startswith("sk-or-v1-")
    
    # Try structured outputs first (OpenAI) or JSON mode (OpenRouter)
    try:
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_input}
        ]
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,  # Reduced to work within credit limits
        }
        
        # Use structured outputs if response_format provided (Pydantic schema)
        if response_format:
            if not is_openrouter:
                # OpenAI structured outputs
                kwargs["response_format"] = response_format
            else:
                # OpenRouter uses JSON mode with schema
                kwargs["response_format"] = {"type": "json_object"}
        
        last_error = None
        content = None
        for attempt in range(max_retries):
            try:
                resp = client.chat.completions.create(**kwargs)
                content = resp.choices[0].message.content
                
                if not content:
                    # Empty response - retry if we have attempts left
                    if attempt < max_retries - 1:
                        delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"⚠️  Empty response (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        # Last attempt failed - use default response
                        print(f"⚠️  Empty response after {max_retries} attempts, using default values")
                        return {
                            "voice_accuracy": 3,
                            "style_marker_coverage": 0.5,
                            "persona_consistency": 3,
                            "clarity": 3,
                            "overfitting_to_mbti": 2,
                            "rationales": ["Empty response from model - using defaults"],
                            "cues": []
                        }
                break  # Success, exit retry loop
            except Exception as e:
                last_error = e
                error_str = str(e)
                error_code = None
                
                # Check if it's a 402 error (insufficient credits)
                if "402" in error_str or "Insufficient credits" in error_str:
                    error_code = 402
                elif hasattr(e, 'status_code'):
                    error_code = e.status_code
                elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    error_code = e.response.status_code
                
                # Retry on 402 errors (might be temporary)
                if error_code == 402 and attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"⚠️  402 error (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                
                # For other errors or final attempt, raise
                if attempt == max_retries - 1:
                    raise
                raise
        
        if not content:
            # Fallback default response
            print(f"⚠️  Empty response after all attempts, using default values")
            return {
                "voice_accuracy": 3,
                "style_marker_coverage": 0.5,
                "persona_consistency": 3,
                "clarity": 3,
                "overfitting_to_mbti": 2,
                "rationales": ["Empty response from model - using defaults"],
                "cues": []
            }
        
        # Parse JSON response
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            parsed = {"raw_response": str(parsed)}
        
        return parsed
        
    except Exception as e:
        # Fallback to text-based parsing
        text = call_model_text(client, model, instructions, user_input, reasoning_effort=reasoning_effort)
        
        if not text or not text.strip():
            # Return default response instead of crashing
            print(f"⚠️  Empty response in fallback, using default values")
            return {
                "voice_accuracy": 3,
                "style_marker_coverage": 0.5,
                "persona_consistency": 3,
                "clarity": 3,
                "overfitting_to_mbti": 2,
                "rationales": ["Empty response from model - using defaults"],
                "cues": []
            }
        
        try:
            parsed = json.loads(text)
            # Ensure parsed is a dict
            if not isinstance(parsed, dict):
                # If it's not a dict, try to wrap it or return default
                parsed = {"raw_response": str(parsed)}
            
            # Handle nested structures - extract evaluation if present
            if isinstance(parsed, dict) and "evaluation" in parsed:
                eval_data_raw = parsed.get("evaluation", {})
                # Ensure eval_data is a dict, not a string or other type
                if isinstance(eval_data_raw, dict):
                    eval_data = eval_data_raw
                elif isinstance(eval_data_raw, str):
                    # Try to parse if it's a JSON string
                    try:
                        eval_data = json.loads(eval_data_raw)
                        if not isinstance(eval_data, dict):
                            eval_data = {}
                    except:
                        eval_data = {}
                else:
                    eval_data = {}
                
                # Try to map common evaluation formats to our schema
                # Final safety check - ensure eval_data is definitely a dict
                if not isinstance(eval_data, dict):
                    eval_data = {}
                
                result = {}
                # Safe access with explicit type checking
                voice_score = eval_data.get("voice_score", 3) if isinstance(eval_data, dict) else 3
                result["voice_accuracy"] = eval_data.get("voice_accuracy", voice_score) if isinstance(eval_data, dict) else 3
                
                if isinstance(eval_data, dict) and eval_data:
                    style_coverage = len([k for k in eval_data.keys() if eval_data.get(k) is True]) / 4.0
                else:
                    style_coverage = 0.5
                result["style_marker_coverage"] = eval_data.get("style_marker_coverage", style_coverage) if isinstance(eval_data, dict) else 0.5
                
                consistency_val = eval_data.get("consistency", 3) if isinstance(eval_data, dict) else 3
                result["persona_consistency"] = eval_data.get("persona_consistency", consistency_val) if isinstance(eval_data, dict) else 3
                result["clarity"] = eval_data.get("clarity", 3) if isinstance(eval_data, dict) else 3
                
                overfitting_val = eval_data.get("overfitting", 2) if isinstance(eval_data, dict) else 2
                result["overfitting_to_mbti"] = eval_data.get("overfitting_to_mbti", overfitting_val) if isinstance(eval_data, dict) else 2
                result["rationales"] = parsed.get("rationales", parsed.get("commentary", {}).values() if isinstance(parsed.get("commentary"), dict) else ["See evaluation"])
                result["cues"] = parsed.get("cues", list(parsed.get("commentary", {}).keys())[:5] if isinstance(parsed.get("commentary"), dict) else ["See evaluation"])
                return result
            return parsed
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            import re
            # Strategy 1: Match ```json ... ``` or ``` ... ``` with JSON inside
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        
        if not json_match:
            # Strategy 2: Match any content between ``` markers, then extract JSON
            code_block_match = re.search(r'```[^\n]*\n(.*?)```', text, re.DOTALL)
            if code_block_match:
                inner_text = code_block_match.group(1).strip()
                # Find first { and last } in the inner text
                start = inner_text.find("{")
                end = inner_text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    # Create a mock match object
                    class MockMatch:
                        def group(self, n):
                            return inner_text[start:end+1] if n == 1 else None
                    json_match = MockMatch()
        
        if not json_match:
            # Strategy 3: If text starts with ```json, try to extract everything after it
            if text.strip().startswith("```json") or text.strip().startswith("```"):
                # Remove the opening ```json or ```
                cleaned = re.sub(r'^```(?:json)?\s*\n?', '', text.strip(), flags=re.MULTILINE)
                # Remove closing ```
                cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
                # Find first { and last }
                start = cleaned.find("{")
                end = cleaned.rfind("}")
                if start != -1 and end != -1 and end > start:
                    class MockMatch:
                        def group(self, n):
                            return cleaned[start:end+1] if n == 1 else None
                    json_match = MockMatch()
        
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                # Ensure parsed is a dict
                if not isinstance(parsed, dict):
                    parsed = {"raw_response": str(parsed)}
                
                eval_data_raw = {}
                if isinstance(parsed, dict) and "evaluation" in parsed:
                    # Apply same transformation as above
                    eval_data_raw = parsed.get("evaluation", {})
                # Handle eval_data as string, dict, or other
                if isinstance(eval_data_raw, dict):
                    eval_data = eval_data_raw
                elif isinstance(eval_data_raw, str):
                    try:
                        eval_data = json.loads(eval_data_raw)
                        if not isinstance(eval_data, dict):
                            eval_data = {}
                    except:
                        eval_data = {}
                else:
                    eval_data = {}
                
                # Final safety check
                if not isinstance(eval_data, dict):
                    eval_data = {}
                
                result = {
                    "voice_accuracy": eval_data.get("voice_accuracy", 3) if isinstance(eval_data, dict) else 3,
                    "style_marker_coverage": 0.5,
                    "persona_consistency": 3,
                    "clarity": 3,
                    "overfitting_to_mbti": 2,
                    "rationales": ["Extracted from nested structure"],
                    "cues": ["See evaluation"]
                }
                return result
            except json.JSONDecodeError:
                pass
        
        # last-ditch cleanup - find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(text[start:end+1])
                # Ensure parsed is a dict
                if not isinstance(parsed, dict):
                    parsed = {"raw_response": str(parsed)}
                
                eval_data_raw = {}
                if isinstance(parsed, dict) and "evaluation" in parsed:
                    eval_data_raw = parsed.get("evaluation", {})
                # Handle eval_data as string, dict, or other
                if isinstance(eval_data_raw, dict):
                    eval_data = eval_data_raw
                elif isinstance(eval_data_raw, str):
                    try:
                        eval_data = json.loads(eval_data_raw)
                        if not isinstance(eval_data, dict):
                            eval_data = {}
                    except:
                        eval_data = {}
                else:
                    eval_data = {}
                
                # Final safety check
                if not isinstance(eval_data, dict):
                    eval_data = {}
                
                result = {
                    "voice_accuracy": eval_data.get("voice_accuracy", 3) if isinstance(eval_data, dict) else 3,
                    "style_marker_coverage": 0.5,
                    "persona_consistency": 3,
                    "clarity": 3,
                    "overfitting_to_mbti": 2,
                    "rationales": ["Extracted from nested structure"],
                    "cues": ["See evaluation"]
                }
                return result
            except json.JSONDecodeError:
                pass
        
        # If all else fails, try one more time with better markdown extraction
        # Sometimes the response is just markdown code blocks
        if "```json" in text or "```" in text:
            # Extract everything between first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(text[start:end+1])
                    if isinstance(parsed, dict):
                        # Handle evaluation field if present
                        if "evaluation" in parsed:
                            eval_data_raw = parsed.get("evaluation", {})
                            if isinstance(eval_data_raw, dict):
                                eval_data = eval_data_raw
                            elif isinstance(eval_data_raw, str):
                                try:
                                    eval_data = json.loads(eval_data_raw)
                                    if not isinstance(eval_data, dict):
                                        eval_data = {}
                                except:
                                    eval_data = {}
                            else:
                                eval_data = {}
                            
                            if not isinstance(eval_data, dict):
                                eval_data = {}
                            
                            return {
                                "voice_accuracy": eval_data.get("voice_accuracy", 3) if isinstance(eval_data, dict) else 3,
                                "style_marker_coverage": eval_data.get("style_marker_coverage", 0.5) if isinstance(eval_data, dict) else 0.5,
                                "persona_consistency": eval_data.get("persona_consistency", 3) if isinstance(eval_data, dict) else 3,
                                "clarity": eval_data.get("clarity", 3) if isinstance(eval_data, dict) else 3,
                                "overfitting_to_mbti": eval_data.get("overfitting_to_mbti", 2) if isinstance(eval_data, dict) else 2,
                                "rationales": ["Extracted from markdown"],
                                "cues": ["See evaluation"]
                            }
                        return parsed
                except:
                    pass
        
        # If all else fails, print debug info and return a default structure
        print(f"Warning: Could not parse JSON from judge response. First 200 chars: {text[:200]}")
        # Don't raise - return default instead to allow experiment to continue
        return {
            "voice_accuracy": 3,
            "style_marker_coverage": 0.5,
            "persona_consistency": 3,
            "clarity": 3,
            "overfitting_to_mbti": 2,
            "rationales": ["JSON parse error: Could not extract valid JSON from response"],
            "cues": ["Parse error"]
        }


# -----------------------------
# Core experiment
# -----------------------------

def load_existing_results(csv_path: str) -> set:
    """Load existing results and return a set of (persona_key, prompt_id, mbti, use_mbti) tuples."""
    completed = set()
    if not os.path.exists(csv_path):
        return completed
    
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                persona_key = row.get("persona_key", "")
                prompt_id = str(row.get("prompt_id", ""))  # Convert to string for consistency
                mbti = row.get("mbti", "")
                # Handle both string "True"/"False" and boolean values
                use_mbti_val = row.get("use_mbti", "")
                if isinstance(use_mbti_val, str):
                    use_mbti = use_mbti_val.lower() == "true"
                else:
                    use_mbti = bool(use_mbti_val)
                # Create unique key for this trial
                trial_key = (persona_key, prompt_id, mbti, use_mbti)
                completed.add(trial_key)
    except Exception as e:
        print(f"⚠️  Warning: Could not load existing results from {csv_path}: {e}")
        print("   Starting fresh...")
    
    return completed

def build_generation_prompt(persona: Persona, mbti: Optional[str], user_prompt: str, use_mbti: bool = True) -> str:
    """Build generation prompt with or without MBTI overlay."""
    if use_mbti and mbti:
        return STANDARD_PROMPT_TEMPLATE.format(
            name=persona.name,
            domain=persona.domain,
            era=persona.era,
            voice=persona.voice,
            signature_moves=persona.signature_moves,
            avoid=persona.avoid,
            mbti=mbti,
            user_prompt=user_prompt
        )
    else:
        return CONTROL_PROMPT_TEMPLATE.format(
            name=persona.name,
            domain=persona.domain,
            era=persona.era,
            voice=persona.voice,
            signature_moves=persona.signature_moves,
            avoid=persona.avoid,
            user_prompt=user_prompt
        )

def assess_persona_mbti(client: OpenAI, persona: Persona, model: str) -> Dict[str, Any]:
    """Assess what MBTI type the persona actually is based on their characteristics."""
    assessment_prompt = f"""Assess the MBTI type of this historical figure based on their documented characteristics, writing style, and intellectual approach.

Persona: {persona.name}
Domain: {persona.domain}
Era/Context: {persona.era}
Voice characteristics: {persona.voice}
Signature moves: {persona.signature_moves}
Style markers: {', '.join(persona.style_markers)}
What to avoid: {persona.avoid}

Based on these characteristics, determine the most likely MBTI type:
- I/E: Introversion vs Extraversion (preference for internal vs external focus)
- S/N: Sensing vs Intuition (concrete details vs abstract patterns)
- T/F: Thinking vs Feeling (logic vs values in decision-making)
- J/P: Judging vs Perceiving (structured vs flexible approach)

Return ONLY valid JSON with this structure:
{{
  "mbti_type": "INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP",
  "confidence": 1-5,
  "reasoning": "Detailed explanation of why this MBTI type fits (50+ words)"
}}
"""

    assessment_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "mbti_assessment",
            "strict": True,
            "schema": MBTIAssessmentResult.model_json_schema(),
            "description": "MBTI type assessment for historical persona"
        }
    }
    
    try:
        result = call_model_json(
            client,
            model=model,
            instructions="You are an expert in personality psychology and historical analysis. Assess the MBTI type based on documented characteristics.",
            user_input=assessment_prompt,
            reasoning_effort="low",
            response_format=assessment_schema,
        )
        return result
    except Exception as e:
        # Fallback if assessment fails
        return {
            "mbti_type": "UNKNOWN",
            "confidence": 1,
            "reasoning": f"Assessment failed: {str(e)[:200]}"
        }

def build_judge_prompt(persona: Persona, mbti: str, user_prompt: str, assistant_output: str) -> str:
    markers = "\n".join([f"- {m}" for m in persona.style_markers])
    return f"""Evaluate the assistant output against the persona voice spec.

Persona: {persona.name}
Voice spec: {persona.voice}
Signature moves: {persona.signature_moves}
Avoid: {persona.avoid}
Expected style markers:
{markers}

User prompt:
{user_prompt}

MBTI overlay used (for your awareness): {mbti}

Assistant output:
{assistant_output}
"""

def run_experiment(
    out_jsonl: str = "mbti_voice_results.jsonl",
    out_csv: str = "mbti_voice_results.csv",
    test_prompts: Optional[List[str]] = None,
    generation_model: Optional[str] = None,
    judge_model: Optional[str] = None,
    sleep_s: float = 0.2,
) -> None:
    client = openai_client()
    # Default models: use OpenRouter format if OpenRouter key detected, else OpenAI
    default_model = "openai/gpt-oss-120b" if os.getenv("OPENROUTER_API_KEY") or (os.getenv("OPENAI_API_KEY", "").startswith("sk-or-v1-")) else "gpt-oss-120b"
    gen_model = generation_model or os.getenv("OPENAI_MODEL", default_model)
    j_model = judge_model or os.getenv("OPENAI_JUDGE_MODEL", default_model)
    prompts = test_prompts or DEFAULT_TEST_PROMPTS

    # CSV header
    fieldnames = [
        "persona_key","persona_name","mbti","assessed_mbti","mbti_match","use_mbti","prompt_id","prompt",
        "generated_text",
        "voice_accuracy","style_marker_coverage","persona_consistency","clarity","overfitting_to_mbti",
        "rationales","cues"
    ]

    # Load existing results to resume from where we left off
    completed_trials = load_existing_results(out_csv)
    file_exists = os.path.exists(out_csv) and len(completed_trials) > 0
    
    if file_exists:
        print(f"📊 Found {len(completed_trials)} existing trials. Resuming from where we left off...")
        print(f"   Existing results file: {out_csv}")
    else:
        print("🆕 Starting fresh experiment...")

    # Open files in append mode if they exist, otherwise write mode
    file_mode_jsonl = "a" if file_exists else "w"
    file_mode_csv = "a" if file_exists else "w"
    
    with open(out_jsonl, file_mode_jsonl, encoding="utf-8") as f_jsonl, open(out_csv, file_mode_csv, encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        # Only write header if file is new
        if not file_exists:
            writer.writeheader()

        # Assess each persona's MBTI type once (cache for all trials)
        persona_mbti_assessments = {}
        print("Assessing persona MBTI types...")
        for persona in PERSONAE:
            try:
                assessment = assess_persona_mbti(client, persona, j_model)
                try:
                    assessed_result = MBTIAssessmentResult(**assessment)
                    persona_mbti_assessments[persona.key] = assessed_result.mbti_type
                    print(f"  {persona.name}: {assessed_result.mbti_type} (confidence: {assessed_result.confidence}/5)")
                except Exception as e:
                    persona_mbti_assessments[persona.key] = "UNKNOWN"
                    print(f"  {persona.name}: Assessment validation failed - {str(e)[:100]}")
            except Exception as e:
                persona_mbti_assessments[persona.key] = "UNKNOWN"
                print(f"  {persona.name}: Assessment API call failed - {str(e)[:100]}")
            time.sleep(sleep_s * 2)  # Longer delay for assessments
        print()

        for persona in PERSONAE:
            assessed_mbti = persona_mbti_assessments.get(persona.key, "UNKNOWN")
            # Run control condition (no MBTI) first
            for pi, user_prompt in enumerate(prompts):
                use_mbti = False
                mbti = "NONE"
                
                # Check if this trial is already completed
                trial_key = (persona.key, str(pi), mbti, use_mbti)
                if trial_key in completed_trials:
                    print(f"⏭️  Skipping {persona.name} (control, prompt {pi}) - already completed")
                    continue
                
                gen_prompt = build_generation_prompt(persona, None, user_prompt, use_mbti=False)
                generated = call_model_text(
                    client,
                    model=gen_model,
                    instructions="You are generating the faculty agent's reply. Follow the persona and constraints.",
                    user_input=gen_prompt,
                    reasoning_effort="low",
                ).strip()

                judge_prompt = build_judge_prompt(persona, mbti, user_prompt, generated)

                # Add explicit JSON requirement to judge prompt
                judge_prompt_with_json = judge_prompt + "\n\nIMPORTANT: You must respond with ONLY valid JSON, no explanatory text before or after."
                    
                # Use structured outputs with Pydantic schema
                judge_schema = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "judge_result",
                        "strict": True,
                        "schema": JudgeResult.model_json_schema(),
                        "description": "Evaluation of assistant output against persona voice spec"
                    }
                }
                
                judge_raw = call_model_json(
                    client,
                    model=j_model,
                    instructions=JUDGE_INSTRUCTIONS,
                    user_input=judge_prompt_with_json,
                    reasoning_effort="low",
                    response_format=judge_schema,
                )

                judge = None
                validation_error = None
                try:
                    judge = JudgeResult(**judge_raw)
                except ValidationError as ve:
                    validation_error = ve

                # Calculate MBTI match
                mbti_match = "N/A"
                if assessed_mbti != "UNKNOWN":
                    mbti_match = "MATCH" if mbti == assessed_mbti else "MISMATCH"
                
                row = {
                    "persona_key": persona.key,
                    "persona_name": persona.name,
                    "mbti": mbti,
                    "assessed_mbti": assessed_mbti,
                    "mbti_match": mbti_match,
                    "use_mbti": use_mbti,
                    "prompt_id": pi,
                    "prompt": user_prompt,
                    "generated_text": generated,
                }

                if judge is not None:
                    row.update({
                        "voice_accuracy": judge.voice_accuracy,
                        "style_marker_coverage": judge.style_marker_coverage,
                        "persona_consistency": judge.persona_consistency,
                        "clarity": judge.clarity,
                        "overfitting_to_mbti": judge.overfitting_to_mbti,
                        "rationales": json.dumps(judge.rationales, ensure_ascii=False),
                        "cues": json.dumps(judge.cues, ensure_ascii=False),
                    })
                else:
                    error_msg = str(validation_error) if validation_error else "Unknown error"
                    row.update({
                        "voice_accuracy": -1,
                        "style_marker_coverage": -1,
                        "persona_consistency": -1,
                        "clarity": -1,
                        "overfitting_to_mbti": -1,
                        "rationales": json.dumps(["JUDGE_PARSE_ERROR", error_msg], ensure_ascii=False),
                        "cues": json.dumps([str(judge_raw)[:500] if judge_raw else "No response"], ensure_ascii=False),
                    })

                # JSONL record (full)
                record = {
                    **row,
                    "persona": {
                        "domain": persona.domain,
                        "era": persona.era,
                        "voice": persona.voice,
                        "signature_moves": persona.signature_moves,
                        "avoid": persona.avoid,
                        "style_markers": persona.style_markers,
                    },
                    "models": {"generation": gen_model, "judge": j_model},
                    "timestamp_unix": int(time.time()),
                }

                f_jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
                writer.writerow(row)
                f_csv.flush()
                f_jsonl.flush()

                if sleep_s:
                    time.sleep(sleep_s)
            
            # Run MBTI trials for each MBTI type
            for mbti in MBTI_TYPES:
                for pi, user_prompt in enumerate(prompts):
                    use_mbti = True
                    
                    # Check if this trial is already completed
                    trial_key = (persona.key, str(pi), mbti, use_mbti)
                    if trial_key in completed_trials:
                        print(f"⏭️  Skipping {persona.name} ({mbti}, prompt {pi}) - already completed")
                        continue
                    
                    gen_prompt = build_generation_prompt(persona, mbti, user_prompt, use_mbti=True)
                    generated = call_model_text(
                        client,
                        model=gen_model,
                        instructions="You are generating the faculty agent's reply. Follow the persona and constraints.",
                        user_input=gen_prompt,
                        reasoning_effort="low",
                    ).strip()

                    judge_prompt = build_judge_prompt(persona, mbti, user_prompt, generated)

                    # Add explicit JSON requirement to judge prompt
                    judge_prompt_with_json = judge_prompt + "\n\nIMPORTANT: You must respond with ONLY valid JSON, no explanatory text before or after."
                        
                    # Use structured outputs with Pydantic schema
                    judge_schema = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "judge_result",
                            "strict": True,
                            "schema": JudgeResult.model_json_schema(),
                            "description": "Evaluation of assistant output against persona voice spec"
                        }
                    }
                    
                    judge_raw = call_model_json(
                        client,
                        model=j_model,
                        instructions=JUDGE_INSTRUCTIONS,
                        user_input=judge_prompt_with_json,
                        reasoning_effort="low",
                        response_format=judge_schema,
                    )

                    judge = None
                    validation_error = None
                    try:
                        judge = JudgeResult(**judge_raw)
                    except ValidationError as ve:
                        validation_error = ve

                    # Calculate MBTI match
                    mbti_match = "N/A"
                    if assessed_mbti != "UNKNOWN":
                        mbti_match = "MATCH" if mbti == assessed_mbti else "MISMATCH"
                    
                    row = {
                        "persona_key": persona.key,
                        "persona_name": persona.name,
                        "mbti": mbti,
                        "assessed_mbti": assessed_mbti,
                        "mbti_match": mbti_match,
                        "use_mbti": use_mbti,
                        "prompt_id": pi,
                        "prompt": user_prompt,
                        "generated_text": generated,
                    }

                    if judge is not None:
                        row.update({
                            "voice_accuracy": judge.voice_accuracy,
                            "style_marker_coverage": judge.style_marker_coverage,
                            "persona_consistency": judge.persona_consistency,
                            "clarity": judge.clarity,
                            "overfitting_to_mbti": judge.overfitting_to_mbti,
                            "rationales": json.dumps(judge.rationales, ensure_ascii=False),
                            "cues": json.dumps(judge.cues, ensure_ascii=False),
                        })
                    else:
                        error_msg = str(validation_error) if validation_error else "Unknown error"
                        row.update({
                            "voice_accuracy": -1,
                            "style_marker_coverage": -1,
                            "persona_consistency": -1,
                            "clarity": -1,
                            "overfitting_to_mbti": -1,
                            "rationales": json.dumps(["JUDGE_PARSE_ERROR", error_msg], ensure_ascii=False),
                            "cues": json.dumps([str(judge_raw)[:500] if judge_raw else "No response"], ensure_ascii=False),
                        })

                    # JSONL record (full)
                    record = {
                        **row,
                        "persona": {
                            "domain": persona.domain,
                            "era": persona.era,
                            "voice": persona.voice,
                            "signature_moves": persona.signature_moves,
                            "avoid": persona.avoid,
                            "style_markers": persona.style_markers,
                        },
                        "models": {"generation": gen_model, "judge": j_model},
                        "timestamp_unix": int(time.time()),
                    }

                    f_jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
                    writer.writerow(row)
                    f_csv.flush()
                    f_jsonl.flush()

                    if sleep_s:
                        time.sleep(sleep_s)

    # Final summary
    final_completed = load_existing_results(out_csv)
    total_expected = len(PERSONAE) * len(prompts) * (1 + len(MBTI_TYPES))  # 1 control + 16 MBTI per persona/prompt
    print(f"\n✅ Done.")
    print(f"   Total trials completed: {len(final_completed)} / {total_expected}")
    print(f"   Results written to:\n   - {out_jsonl}\n   - {out_csv}\n")


# -----------------------------
# Optional: quick aggregation
# -----------------------------

def summarize(csv_path: str = "mbti_voice_results.csv") -> None:
    """
    Prints average voice_accuracy per persona and per MBTI.
    """
    from collections import defaultdict

    per_persona = defaultdict(lambda: {"sum":0, "n":0})
    per_mbti = defaultdict(lambda: {"sum":0, "n":0})

    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                s = int(row["voice_accuracy"])
            except Exception:
                continue
            if s < 0:
                continue
            per_persona[row["persona_name"]]["sum"] += s
            per_persona[row["persona_name"]]["n"] += 1
            per_mbti[row["mbti"]]["sum"] += s
            per_mbti[row["mbti"]]["n"] += 1

    print("\nAverage voice_accuracy by persona:")
    for k, v in sorted(per_persona.items(), key=lambda kv: kv[1]["sum"]/max(1,kv[1]["n"]), reverse=True):
        avg = v["sum"]/max(1,v["n"])
        print(f"- {k:18s} {avg:.2f} (n={v['n']})")

    print("\nAverage voice_accuracy by MBTI:")
    for k, v in sorted(per_mbti.items(), key=lambda kv: kv[1]["sum"]/max(1,kv[1]["n"]), reverse=True):
        avg = v["sum"]/max(1,v["n"])
        print(f"- {k:4s} {avg:.2f} (n={v['n']})")


if __name__ == "__main__":
    # Run:
    #   python mbti_voice_eval.py
    # Increased sleep delay to 1.0s to avoid rate limiting
    run_experiment(sleep_s=1.0)

    # Optional quick summary:
    summarize()
