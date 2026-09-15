# Human Evaluation Rubric

This rubric is designed for human annotators to score the quality of the AI Support Agent's outputs.

## Rating Scale (1-5)
All dimensions (except the binary unsupported claim flag) are scored on a 1-5 scale:
- **1 = Poor:** Completely fails the requirement.
- **2 = Needs Improvement:** Has significant flaws but contains some merit.
- **3 = Acceptable:** Meets the minimum requirements safely, but lacks polish.
- **4 = Good:** High quality, minor flaws.
- **5 = Excellent:** Perfect execution.

## Dimensions

### 1. Relevance
- **Definition:** Does the reply directly address the customer's specific question or issue?
- **1:** Completely ignores the prompt.
- **5:** Directly and concisely addresses the core issue.

### 2. Correctness
- **Definition:** Is the technical information or policy stated factually accurate according to company standards?
- **1:** Dangerously incorrect or states the opposite of policy.
- **5:** Perfectly accurate.

### 3. Grounding
- **Definition:** Is the reply based *strictly* on the retrieved historical evidence?
- **1:** Ignored the evidence entirely and hallucinated a response.
- **5:** Perfectly integrated the evidence without adding any unverified details.

### 4. Helpfulness
- **Definition:** Does this reply actually move the customer closer to a resolution?
- **1:** Frustrating, cyclical, or useless.
- **5:** Provides a clear path to resolution or the exact answer.

### 5. Escalation Appropriateness
- **Definition:** Did the agent make the correct decision to auto-handle or escalate?
- **1:** Dangerously auto-handled a high-risk case, or escalated a trivial case for no reason.
- **5:** Made the perfect routing decision based on the evidence available.

### 6. Unsupported Claim (Binary)
- **0 = False:** No hallucinations detected.
- **1 = True:** The agent hallucinated prices, links, dates, or policies not present in the evidence.
