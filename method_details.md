# RL-PPO
Proximal Policy Optimization implementation based on CleanRL (https://docs.cleanrl.dev/). Trained for 1M environment steps. Policy takes environment state vector as input.

# RL-SAC
Soft Actor-Critic implementation based on CleanRL (https://docs.cleanrl.dev/). Trained for 1M environment steps. Policy takes environment state vector as input.

## Diffusion Policy
Diffusion Policy implementation based on LeRobot (https://github.com/huggingface/lerobot). Trained with 110-115 demonstrations per environment. Policy takes images as input.

## LLM Planning
LLM planning with given parameterized skills. We use GPT-5. States are represented as dictionaries mapping objects to features to values.

## VLM Planning
VLM planning with given parameterized skills. We use GPT-5. States are represented as dictionaries mapping objects to features to values. Images are additionally included in the prompt.

## Bilevel Planning
Search-then-sample bilevel planning with given parameterized skills, operators, predicates, and samplers. States are represented as dictionaries mapping objects to features to values.

