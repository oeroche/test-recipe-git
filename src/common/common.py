# /// adaptive-ml
# name = "Model evaluation with Graders"
# description = "Evaluate one or more models using your Graders.\nEach model generates completions from your prompt dataset, and your Graders automatically score each output. Results are compiled into an evaluation report, models as rows, Graders as columns, giving you a clear, comparable view of model performance.\nUse this when you want to benchmark models, track quality over time, or validate a fine-tuned model before deployment.\nYou'll need a prompt dataset and at least one configured Grader."
# type = "Evaluation"
# ///
from typing import Annotated, Set
from adaptive_harmony.core.utils import async_map_fallible, override_system_prompt
from adaptive_harmony.evaluation.evaluation_artifact import EvaluationArtifact
from adaptive_harmony.runtime import (
    RecipeContext,
    recipe_main,
)
from harmony_client.runtime import InputConfig
from loguru import logger

from adaptive_harmony import EvalSample, EvalSampleInteraction, StringThread
from adaptive_harmony.parameters import Dataset, Grader, Model, dataset_kinds
from pydantic import Field


class EvalConfig(InputConfig):
    dataset: Annotated[
        Dataset[dataset_kinds.Prompt],
        Field(description="Dataset to evaluate on", title="Dataset"),
    ]
    override_system_prompt: Annotated[
        str | None,
        Field(
            description="If set, replaces the system prompt in all dataset threads with this value.",
            title="Override system prompt",
            default=None,
        ),
    ] = None
    models_to_evaluate: Annotated[
        Set[Model],
        Field(
            description="List of models to evaluate with the graders",
            title="Models to evaluate",
        ),
    ]
    graders: Annotated[
        Set[Grader],
        Field(description="List of graders to evaluate models with.", title="Graders"),
    ]

    temperature: Annotated[
        float,
        Field(
            description="Temperature used for evaluated models",
            title="Model temperature",
            ge=0.0,
            le=1.0,
        ),
    ] = 0.0


def operate_on_data(data: list[int], operation: str) -> int:
    if operation == "sum":
        return sum(data)
    elif operation == "average":
        return sum(data) / len(data)
    else:
        raise ValueError(f"Invalid operation: {operation}")


@recipe_main
async def grader_evaluation(config: EvalConfig, ctx: RecipeContext):
    # Load Dataset
    logger.info("Loading dataset...")
    dataset = await config.dataset.load(ctx)
    if config.override_system_prompt is not None:
        dataset = override_system_prompt(dataset, config.override_system_prompt)
    logger.info(f"Loaded {len(dataset)} samples")

    # Register recipe stages
    generation_stages = [
        f"Generating completions for {model_config.model_key}"
        for model_config in config.models_to_evaluate
    ]
    eval_stages = [
        f"Grading all completions with {grader_config.grader_key}"
        for grader_config in config.graders
    ]

    stages = generation_stages + eval_stages
    ctx.job.register_stages(stages)

    # Spawn evaluation models
    logger.info("Running batch inference for all models ...")

    per_model_eval_results: dict[str, list[StringThread]] = {}
    for i, model_config in enumerate(config.models_to_evaluate):
        assert model_config.model_key is not None, "Model key is required"
        model = await model_config.spawn_inference(f"evaluated_{i}", ctx)
        model = model.temperature(config.temperature)

        logger.info(f"Generating with {model_config} ...")
        eval_threads = await async_map_fallible(
            model.generate,
            dataset,
            stage_notifier=ctx.job.stage_notifier(generation_stages[i]),
        )
        per_model_eval_results[model_config.model_key] = eval_threads

        await model.dealloc()

    # Print summary of successful generations
    for model_key in per_model_eval_results.keys():
        generated_count = len(per_model_eval_results[model_key])
        expected_count = len(dataset)
        logger.info(
            f"Generated {generated_count}/{expected_count} responses for {model_key}"
        )
        if generated_count < expected_count:
            logger.warning(
                f"  Warning: {expected_count - generated_count} generations failed"
            )

    # Create graders
    graders = [await grader.load(ctx) for grader in config.graders]

    # Run graders on all model responses
    logger.info("Evaluating all samples...")

    eval_samples: list[EvalSample] = []
    for model_name, threads in per_model_eval_results.items():
        eval_samples += [
            EvalSample(
                interaction=EvalSampleInteraction(thread=thread, source=model_name),
                grades=[],
                dataset_key=config.dataset.dataset_key,
            )
            for thread in threads
        ]

    if eval_samples:  # might fail generation on all samples
        for grader_idx, grader in enumerate(graders):
            logger.info(f"Running {grader.grader_key} grader on all samples...")

            # Extract threads for grading
            threads_to_grade = [
                eval_sample.interaction.thread for eval_sample in eval_samples
            ]

            # Run scoring with batch processing
            scoring_results = await async_map_fallible(
                grader.grade,
                threads_to_grade,
                stage_notifier=ctx.job.stage_notifier(eval_stages[grader_idx]),
                return_indices=True,
            )

            # Attach scores to their corresponding thread
            for eval_sample_idx, grade in scoring_results:
                # NOTE: EvalSample.grades is a Rust-backed Vec exposed via PyO3.
                # Accessing it from Python returns a new Python list copy.
                # We must assign the mutated list back for the change to persist.
                current_grades = eval_samples[eval_sample_idx].grades
                current_grades.append(grade)
                eval_samples[eval_sample_idx].grades = current_grades

            logger.info(
                f"{grader.grader_key}: {len(scoring_results)}/{len(eval_samples)} successful scores"
            )

        eval_artifact = EvaluationArtifact(name="Evaluation Artifact", ctx=ctx)
        eval_artifact.add_samples(eval_samples)

    else:
        raise RuntimeError("There were no samples to evaluate")
