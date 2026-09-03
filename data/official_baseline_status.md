# Official Baseline Status

| Method | Official Repo | Local Path | Import Status | Ready for Official Table 2 | Missing Runtime Pieces |
|---|---|---|---|---|---|
| Erase-and-Check | https://github.com/aounon/certified-llm-safety | external/certified-llm-safety | defenses=ok | yes | A safety filter: Llama-2/3, GPT-3.5, or trained DistilBERT classifier<br>Tokenizer compatible with the safety filter<br>Optional official DistilBERT weights from the authors' Dropbox link<br>GPU recommended by the official README |
| SmoothLLM | https://github.com/arobey1/smooth-llm | external/smooth-llm | lib.perturbations=ok | yes | Vicuna or Llama-2 weights configured in lib/model_configs.py<br>llm-attacks / FastChat stack required by the official experiment runner<br>GPU for local target-model inference |
| ToolEmu | https://github.com/ryoungj/ToolEmu | external/ToolEmu | toolemu=ok | yes | PromptCoder/procoder from https://github.com/dhh1995/PromptCoder<br>ToolEmu Python dependencies such as langchain==0.0.277, transformers, torch, openai, anthropic<br>OPENAI_API_KEY or ANTHROPIC_API_KEY for official emulation/evaluation<br>Its own ToolEmu benchmark assets, not a direct InjecAgent/BIPIA drop-in defense |
| PromptCoder dependency for ToolEmu | https://github.com/dhh1995/PromptCoder | external/PromptCoder | procoder=ok | yes | Installed or on PYTHONPATH before running ToolEmu |

Note: `Ready for Official Table 2` here only means the official code can be imported locally.
A faithful result still requires the official model weights, API keys, and benchmark protocol listed above.
