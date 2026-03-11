
## 1. Overview

The primary artifacts provided are the jailbreak prompts used in the black-box evaluation of 10 widely deployed commercial LLM-integrated applications.

## 2. Repository Contents

This repository contains the following files:

- `Advbench_prompts_top50.json`
  - The 50 harmful instructions selected from AdvBench
  - Used as the base instruction set across all evaluated applications

- Application-specific jailbreak prompts:
  - `WPS.json`
  - `AiPPT.json`
  - `Youdao.json`
  - `Quark.json`
  - `Gamma.json`
  - `Canva.json`
  - `Lark.json`
  - `Brave.json`
  - `Mem.json`
  - `X.json`

Each JSON file contains the concrete prompts submitted to the corresponding application during evaluation.
## 3. Attack
You can run `agent_gap_tester.py` to carry out the attack.

