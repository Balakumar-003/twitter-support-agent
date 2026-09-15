# Intent Labeling Guidelines

## Overview
This document provides guidelines for annotators assigning intents to customer support messages. Accurate labeling is critical for training a reliable support agent classifier.

## Intent Definitions

1. **OS Update / Performance Issues (`os_update_performance`)**
   - **Definition:** Issues related to slow performance, freezing, or bugs after an iOS update.
   - **Positive Example:** "I just updated my phone and suddenly everything takes ages to load"
   - **Negative Example:** "killing my battery within 12 hours" (This is Battery Drain)

2. **Battery Drain (`battery_drain`)**
   - **Definition:** Complaints about the battery dying too quickly or draining fast.
   - **Positive Example:** "used my phone for 2 minutes and it drains it down 8 percent"
   - **Negative Example:** "phone is dead and won't turn on"

3. **App Compatibility / Usage Issues (`app_compatibility`)**
   - **Definition:** Specific apps crashing, not working together, or broken functionality within the OS.
   - **Positive Example:** "does not let me listen to music and go on whatsapp at the same time"
   - **Negative Example:** "my iphone screen is cracked"

4. **Account & Authentication (`account_authentication`)**
   - **Definition:** Issues with receiving codes, logging in, or Apple ID.
   - **Positive Example:** "I need a new code for my I-store"
   - **Negative Example:** "I forgot my password"

5. **Other / Unclear (`other_or_unclear`)**
   - **Definition:** Messages that do not fit into any other intent, lack context, or are not support-related.
   - **Positive Example:** "Do you sell bananas?"
   - **Negative Example:** "My battery is draining fast"

## Ambiguity Policy

### 1. Multi-Intent Policy
If a message matches multiple intents (e.g., "#ios11update - is still killing my battery"), apply the highest priority intent according to the following hierarchy:
1. Account & Authentication (Highest Priority)
2. Battery Drain
3. OS Update / Performance Issues
4. App Compatibility / Usage Issues
5. Other / Unclear

### 2. Too Short / Lack of Context
If a message is too short (e.g., "Help", "It's broken") and provides no context for the issue, assign `other_or_unclear`. Do not guess the intent.

### 3. Abusive or Urgent Messages
If a message is abusive (e.g., "I used my fucking phone..."), ignore the sentiment and label the core intent (in this case, `battery_drain`). Emotion is not an intent. 

### 4. Unrelated to Support
If a message is entirely unrelated to AppleSupport products, assign `other_or_unclear`.

## Annotation Workflow
1. Read the customer message carefully.
2. Identify the core problem.
3. Check against the exclusion rules of the candidate intent.
4. Assign the highest-priority intent if multiple apply.
5. If no intent fits confidently, assign `other_or_unclear`.

## Quality Control Rules
- **Consistency:** Always follow the multi-intent priority list.
- **Evidence:** Do not infer a problem if it is not explicitly stated in the text.
- **Review:** Periodically review a random sample of `other_or_unclear` labels to ensure no new patterns (e.g., Hardware Issues) are emerging that require a new intent category.
