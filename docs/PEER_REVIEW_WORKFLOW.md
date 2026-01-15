# Peer Review Workflow

This document describes the peer review workflow for research papers in this repository.

## Workflow Overview

1. **Initial Review** - Reviewers provide peer review on GitHub issues
2. **Author Response** - Author responds to reviews and makes revisions
3. **Re-Review** - Reviewers review the revised paper

## Issue Structure

Each reviewer has ONE issue that tracks the entire review process:

- **Issue #1**: John Dewey's Review
- **Issue #2**: Alan Turing's Review
- **Issue #3**: Ada Lovelace's Review

Each issue contains:
- **Initial Review**: Original peer review (in issue body)
- **Author Response**: Author's response comment
- **Re-Review Comments**: Reviewers' assessment of revisions (added as comments)

## Reviewing Revised Papers

**Reviewers should use their EXISTING issue, not create new ones.**

To review the revised paper:

1. Check out the merged revision branch:
   ```bash
   git checkout revisions/merged
   ```

2. Review the revised `RESEARCH_PAPER.md` in that branch

3. Add your review as a NEW COMMENT on your existing issue:
   ```bash
   gh issue comment <issue-number> --repo InquiryInstitute/mbti-faculty-voice-research --body-file review_comment.md
   ```

This keeps the full review history together in one place, making it easy to track:
- Original concerns
- How they were addressed
- Final assessment

## Revision Branches

- `revisions/review-1-john-dewey` - Revisions addressing John Dewey's concerns
- `revisions/review-2-alan-turing` - Revisions addressing Alan Turing's concerns
- `revisions/review-3-ada-lovelace` - Revisions addressing Ada Lovelace's concerns
- `revisions/merged` - All revisions merged together (final version for review)

## Final Approval

Once all reviewers approve the revisions, the merged branch can be merged into main:
```bash
git checkout main
git merge revisions/merged
git push origin main
```
