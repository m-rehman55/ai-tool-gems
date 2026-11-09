# MANUAL ASSISTIVE TECHNOLOGY TEST PROTOCOL & VERIFICATION MATRIX

**Project:** AI Tool Gems (`aitoolgems.tech`)  
**Standard:** WCAG 2.2 AA (Guidelines 1.3, 2.1, 2.4, 3.2, 4.1)  
**Governing Issue:** ATG-31-002  
**Target Screen Readers:** NVDA (Windows), VoiceOver (iOS/macOS), TalkBack (Android)  

---

## 1. OBJECTIVE

While automated test suites verify that all 375 buttons possess accessible names and color contrast exceeds AA/AAA thresholds, automated tools cannot verify real-world auditory comprehensibility or touch-navigation ergonomics. This protocol provides human testers with a standardized, reproducible script to evaluate screen-reader behavior across critical customer journeys.

---

## 2. TEST ENVIRONMENT SPECIFICATIONS

| Platform | Assistive Technology | Browser | Hardware Profile |
|---|---|---|---|
| **Desktop 1** | NVDA (v2024.1 or higher) | Google Chrome (Latest Stable) | Windows 11 (x64), 1080p display |
| **Desktop 2** | VoiceOver | Apple Safari (Latest) | macOS Sonoma, Retina display |
| **Mobile 1** | Google TalkBack (v14.0+) | Google Chrome Mobile | Android 13/14, 6.5" AMOLED (390x844 CSS px) |
| **Mobile 2** | iOS VoiceOver | Apple Mobile Safari | iPhone 14/15/16, iOS 17/18 (390x844 CSS px) |

---

## 3. STANDARDIZED TEST JOURNEYS & KEYSTROKE SCRIPTS

### Journey 1: Skip to Content & Main Landmark Discovery
- **URL:** `https://aitoolgems.tech/`
- **Initial State:** Focus on address bar, press `Tab`.
- **Expected Keystroke:** `Tab` (first keystroke on page load).
- **Observed Visual:** "Skip to main content" banner appears in high-contrast focus ring at the top of the viewport.
- **Expected NVDA Speech:** *"Skip to main content, link"*.
- **Action:** Press `Enter`.
- **Verification:** Keyboard focus moves immediately to `<main id="main">`. Pressing `Down Arrow` begins reading the main heading *"Discover Verified AI Tools & Digital Subscriptions in Pakistan, heading level 1"*, skipping navigation links.

---

### Journey 2: Currency Toggle (PKR to USD & Vice Versa)
- **URL:** `https://aitoolgems.tech/` or `/tools/`
- **Action:** Navigate to the currency toggle switch using `Tab`.
- **Expected NVDA Speech:** *"Currency toggle switch, button, pressed: PKR active"*.
- **Action:** Press `Space` or `Enter`.
- **Expected Live Announcement:** *"Switched currency to US Dollars. Prices updated."* or `<span class="sr-only">` price updates announced.
- **Verification:** Product cards update displayed pricing dynamically.

---

### Journey 3: Tool Detail Page & WhatsApp Order Flow
- **URL:** `https://aitoolgems.tech/tools/chatgpt/`
- **Action:** Navigate using heading navigation (`H` key in NVDA).
- **Checkpoints:**
  1. `H1`: *"ChatGPT Plus Subscription in Pakistan"* announced clearly.
  2. Pricing block: *"Current price: 3,500 Pakistani Rupees per month, strikethrough original price 4,000 Rupees, save 13 percent"*.
  3. Action buttons:
     - *"Order via WhatsApp, link"* (Must announce that it opens in a new window or launches external app).
     - *"Visit Official Website, link, external"*.
- **Action:** Activate WhatsApp button.
- **Verification:** Browser launches `https://wa.me/923000000000?text=...` with pre-filled message, preserving focus state upon return.

---

### Journey 4: Modal Dialog Focus Trapping (Tool Finder Quiz)
- **URL:** `https://aitoolgems.tech/`
- **Action:** Activate "Find Your AI Tool" button.
- **Expected Screen Reader Behavior:**
  1. Modal opens with role `dialog` or `aria-modal="true"`.
  2. Accessible name announced: *"AI Tool Finder Quiz, dialog"*.
  3. Focus is automatically transferred to the first interactive element or the Close button.
  4. Pressing `Tab` repeatedly cycles strictly within modal controls (focus does NOT escape to background page).
  5. Pressing `Escape` closes the modal immediately and returns focus to the trigger button on the page.

---

### Journey 5: FAQ Accordion Expand / Collapse
- **URL:** `https://aitoolgems.tech/tools/chatgpt/#faq` or `/faq.html`
- **Action:** Tab to FAQ question header.
- **Expected Speech:** *"How do I receive my ChatGPT login? button, collapsed, aria-expanded false"*.
- **Action:** Press `Enter` or `Space`.
- **Expected Speech:** *"expanded, aria-expanded true"*. Answer text becomes readable in linear reading mode (`Down Arrow`).

---

## 4. HUMAN TEST EXECUTION CHECKLIST

| Test Journey | Desktop NVDA | Desktop VoiceOver | Mobile TalkBack | Mobile VoiceOver | Status |
|---|:---:|:---:|:---:|:---:|:---:|
| 1. Skip to Content | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |
| 2. Currency Switcher | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |
| 3. WhatsApp Purchase Intent | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |
| 4. Tool Finder Modal Trapping | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |
| 5. FAQ Expansion States | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |
| 6. Contrast & Focus Visible | [ ] PASS | [ ] PASS | [ ] PASS | [ ] PASS | READY FOR TESTING |

*Note: Automated DOM accessibility tests are integrated in the CI regression suite (`tests/test_accessibility.py`). Physical execution of this matrix is scheduled for Phase 34.*
