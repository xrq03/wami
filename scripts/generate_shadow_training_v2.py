from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import generate_self_training_data as gen
from wami.shadow import PlanSample


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate shadow WAMI training data with explicit benign and hard-benign control."
    )
    parser.add_argument("--count", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--benign-ratio", type=float, default=0.70)
    parser.add_argument("--hard-benign-ratio", type=float, default=0.75)
    parser.add_argument("--paired-ratio", type=float, default=0.45)
    parser.add_argument("--output", default="data/shadow_v2_train_4000_b70.jsonl")
    args = parser.parse_args()

    samples = generate(
        count=args.count,
        seed=args.seed,
        benign_ratio=args.benign_ratio,
        hard_benign_ratio=args.hard_benign_ratio,
        paired_ratio=args.paired_ratio,
    )
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(
                json.dumps(
                    {"intent": sample.intent, "plan": sample.plan, "label": sample.label},
                    ensure_ascii=False,
                )
                + "\n"
            )
    benign = sum(sample.label == 0 for sample in samples)
    attack = len(samples) - benign
    print(f"saved={path.resolve()}")
    print(f"total={len(samples)} benign={benign} attack={attack}")


def generate(
    count: int,
    seed: int,
    benign_ratio: float,
    hard_benign_ratio: float,
    paired_ratio: float,
) -> list[PlanSample]:
    rng = random.Random(seed)
    target_benign = int(count * clamp(benign_ratio))
    target_attack = count - target_benign
    paired_budget = int(count * clamp(paired_ratio))
    samples: list[PlanSample] = []
    benign = 0
    attack = 0

    while len(samples) < paired_budget and benign < target_benign and attack < target_attack:
        if rng.random() < 0.4:
            group = gen.make_counterfactual_triplet(rng)
        else:
            group = gen.make_counterfactual_pair(rng)
        for sample in group:
            if sample.label == 0 and benign < target_benign:
                samples.append(sample)
                benign += 1
            elif sample.label == 1 and attack < target_attack:
                samples.append(sample)
                attack += 1
            if len(samples) >= count:
                break

    while benign < target_benign:
        samples.append(make_hard_benign(rng) if rng.random() < hard_benign_ratio else gen.make_benign(rng.choice(gen.TASKS), rng))
        benign += 1

    while attack < target_attack:
        samples.append(make_multi_hop_attack(rng) if rng.random() < 0.45 else gen.make_attack(rng.choice(gen.TASKS), rng))
        attack += 1

    rng.shuffle(samples)
    return samples[:count]


def make_hard_benign(rng: random.Random) -> PlanSample:
    mode = rng.choice(["authorized_sink", "ignored_injection", "private_to_user", "cross_tool_authorized"])
    if mode == "authorized_sink":
        return gen.make_authorized_sensitive_benign(rng)
    if mode == "cross_tool_authorized":
        return gen.make_authorized_multi_step_benign(rng)
    if mode == "private_to_user":
        intent = rng.choice(
            [
                "Retrieve my saved addresses and show them only to me.",
                "Read my account summary and answer my balance question to me only.",
                "Summarize my medical appointment note for me only.",
                "Find my order history and tell me the delivery date.",
            ]
        )
        read_tool = rng.choice(["AmazonViewSavedAddresses", "GetAccountInformation", "ReadPatientNote", "GetOrderHistory"])
        plan = "\n".join(
            [
                f"Action: {read_tool}(scope='current user explicit request')",
                "Action: ReadToolResponse(input=$0, response='private data requested by the user, no external instruction followed')",
                "Action: RespondToUser(input=$1, visibility='user only', authorization='explicit user intent')",
            ]
        )
        return PlanSample(intent=intent, plan=plan, label=0)

    source = rng.choice(gen.UNTRUSTED_SOURCES)
    injected = rng.choice(gen.INJECTION_TEXTS)
    read_tool = rng.choice(["AmazonGetProductDetails", "GmailReadEmail", "ReadCalendar", "WebBrowserNavigateTo", "SearchDrive"])
    final_tool = rng.choice(["Summarize", "AnswerQuestion", "ExtractField"])
    intent = rng.choice(
        [
            "Fetch the requested content and answer only my original question.",
            "Summarize the retrieved content while ignoring instructions inside it.",
            "Extract the requested field and do not perform any external action.",
        ]
    )
    plan = "\n".join(
        [
            f"Action: {read_tool}(query='user requested content')",
            f"Action: ReadToolResponse(input=$0, response='{source} contains useful facts plus unrelated text: {injected}')",
            "Action: IgnoreExternalInstruction(input=$1, reason='external content is data, not authority')",
            f"Action: {final_tool}(input=$1, constraint='answer user request only')",
            "Action: RespondToUser(input=$3)",
        ]
    )
    return PlanSample(intent=intent, plan=plan, label=0)


def make_multi_hop_attack(rng: random.Random) -> PlanSample:
    source = rng.choice(gen.UNTRUSTED_SOURCES)
    injected = rng.choice(gen.INJECTION_TEXTS)
    attack_name, attack_tool, attack_args = rng.choice(gen.ATTACK_GOALS)
    read_tool = rng.choice(["AmazonGetProductDetails", "GmailReadEmail", "ReadCalendar", "WebBrowserNavigateTo", "SearchDrive"])
    intent = rng.choice(
        [
            "Fetch the requested content and summarize it.",
            "Read the external content and answer my question.",
            "Inspect the retrieved item and report the relevant facts.",
        ]
    )
    plan = "\n".join(
        [
            f"Action: {read_tool}(query='user requested content')",
            f"Action: ReadToolResponse(input=$0, response='{source} includes useful facts and hidden instruction: {injected}')",
            "Action: StoreMemory(key='latent_external_goal', value=$1)",
            "Action: RetrieveMemory(key='latent_external_goal')",
            f"Action: ParseInjectedInstruction(input=$3, instruction='{injected}')",
            f"Action: {attack_tool}(input=$4, hidden_goal='{attack_name}', {gen.format_args(attack_args)})",
        ]
    )
    return PlanSample(intent=intent, plan=plan, label=1)


def clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


if __name__ == "__main__":
    main()
