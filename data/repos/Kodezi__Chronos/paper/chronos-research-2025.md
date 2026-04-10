# Kodezi Chronos: A Debugging-First Language Model for Repository-Scale Code Understanding

Ishraq Khan, Assad Chowdary, Sharoz Haseeb, Urvish Patel, Yousuf Zaii  
Kodezi Inc.  
{Ishraq,Assad,Sharoz,Urvish,Yousuf}@kodezi.com

## Abstract

Debugging remains unsolved for LLMs despite advances in code generation. While Claude 4.5 Sonnet and Claude 4.1 Opus achieve > 70% on synthesis benchmarks, they fail on real debugging with < 15% success rates (95% CI: 12.1-17.9%). We present Kodezi Chronos, the first debugging-specific language model combining: (1) Adaptive Graph-Guided Retrieval (AGR) navigating codebases up to 10M LOC via multi-hop traversal (92% precision, 85% recall), (2) Persistent Debug Memory (PDM) learning from 15M+ sessions, and (3) 7-layer architecture for iterative fix-test-refine loops.

On 5,000 real-world scenarios, Chronos achieves 67.3% ± 2.1% fix accuracy versus 14.2% ± 1.3% (Claude 4.1 Opus) and 13.8% ± 1.2% (GPT-4.1), with Cohen's d=3.87 effect size. On the SWE-bench Lite benchmark, Chronos achieves state-of-the-art performance with **80.33% resolution rate (241/300 instances)**, establishing a **20 percentage point lead** over the next best system (ExpeRepair-v1.0 + Claude 4.5 Sonnet: 60.33%). Repository-specific performance reaches **96.1% (sympy)**, **93.8% (sphinx)**, and **90.4% (django)**. The system reduces debugging time by 40% and iterations by 65%. Chronos resolves complex multi-file bugs requiring cross-repository understanding and temporal analysis.

Key limitations include 23.4% success on hardware-dependent bugs and 41.2% on dynamic language issues. Theoretical analysis proves O(k log d) retrieval complexity with convergence guarantees. Human evaluation (N=50) shows 89% preference over baselines. Available Q4 2025 (Kodezi OS) and Q1 2026 (API).

## Key Updates from 2025 Research

### Performance Improvements
- **Debug Success Rate**: 67.3% ± 2.1% (up from 65.3%)
- **Human Preference**: 89% in evaluation studies
- **Time Reduction**: 40% faster debugging
- **Iteration Count**: 7.8 average iterations for thorough fixes

### New Comparisons

#### SWE-bench Lite (State-of-the-Art Results)
- **Chronos**: **80.33% (241/300 instances)** - #1 Globally
- **ExpeRepair-v1.0 + Claude 4.5 Sonnet**: 60.33% - #2
- **Claude 4.5 Sonnet (Bash Only)**: ~14%
- **Claude 4.1 Opus (Bash Only)**: 14.2%
- **GPT-4.1**: 13.8%
- **Gemini 2.0 Pro**: 13.4%

**Key Insight**: 20 percentage point absolute lead over second place

#### Repository-Specific Performance (SWE-bench Lite)
- **sympy** (symbolic mathematics): 96.1%
- **sphinx** (documentation): 93.8%
- **django** (web frameworks): 90.4%

#### Code Generation vs Debugging Gap
- Claude 4.5 Sonnet: 72.7% (SWE-bench Full) → ~14% (SWE-bench Lite) = **-58.7pp gap**
- Claude 4.1 Opus: 72.5% (SWE-bench Full) → 14.2% (SWE-bench Lite) = **-58.3pp gap**
- GPT-4.1: 54.6% (SWE-bench Full) → 13.8% (SWE-bench Lite) = **-40.8pp gap**

#### Other Models Evaluated
- Claude 4.1 Opus: 14.2% ± 1.3% success rate (MRR)
- GPT-4.1: 13.8% ± 1.2% success rate (MRR)
- DeepSeek V3: Mentioned for efficient training ($5.6M cost)
- Gemini 2.0 Pro: <15% success rate on debugging

### Architectural Enhancements
- Enhanced AGR with O(k log d) retrieval complexity
- Improved PDM with 15M+ debugging sessions
- 7-layer architecture optimized for debugging workflows
- Cohen's d=3.87 effect size demonstrating large improvement

### Limitations Identified
- 23.4% success on hardware-dependent bugs
- 41.2% success on dynamic language issues
- Still requires significant computational resources