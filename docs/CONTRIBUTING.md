# Contributing to MBTI Faculty Voice Research

Thank you for your interest in contributing to this research project!

## How to Contribute

### Reporting Issues

If you encounter bugs, have questions, or want to suggest improvements:

1. Check existing issues to avoid duplicates
2. Open a new issue with:
   - Clear description
   - Steps to reproduce (if applicable)
   - Expected vs. actual behavior
   - Environment details (Python version, OS, etc.)

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes:**
   - Follow Python style guidelines (PEP 8)
   - Add docstrings to new functions
   - Update documentation as needed
4. **Test your changes:**
   - Run the experiment on a small subset
   - Verify output format is correct
5. **Submit a pull request:**
   - Describe your changes clearly
   - Reference any related issues
   - Include test results if applicable

### Contributing Personae

To add new faculty personae:

1. Add a `Persona` entry to the `PERSONAE` list in `mbti_voice_eval.py`
2. Include:
   - Historical context and era
   - Voice specification
   - Signature moves
   - Avoid patterns
   - Style markers
3. Test with a small subset before full experiment
4. Document in README or separate personae guide

### Contributing Analysis

If you've analyzed the results:

1. Share your analysis scripts (Python, R, Jupyter notebooks)
2. Document methodology
3. Include visualizations
4. Update `ANALYSIS.md` with new insights

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular

### Documentation

- Update README for significant changes
- Add docstrings to new code
- Update SETUP.md if installation changes
- Document new analysis methods in ANALYSIS.md

## Research Ethics

- Ensure faculty personae are represented respectfully
- Acknowledge limitations of MBTI as a psychological tool
- Cite sources appropriately
- Be transparent about methodology

## Questions?

Open an issue with the `question` label, or contact the Inquiry Institute.

Thank you for contributing to this research!
