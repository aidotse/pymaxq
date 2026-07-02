# Hydra

[Hydra](https://hydra.cc/) is a framework for **configuring an application from the outside** instead of hardcoding
values in source. You describe *what objects to build and how to wire them together* in a YAML file, and Hydra
constructs that object graph at runtime — so you can re-run with different parameters (or swap whole components) by
editing config or passing command-line overrides, without touching the code.

This project ships a tiny working example you can read in five minutes: a text-transform pipeline under your package's
`pipeline.py` (shown below with an example package, `my_project`).

## The core idea: `_target_` + `instantiate`

Hydra's headline feature is **`hydra.utils.instantiate`**: any config node with a `_target_` key is turned into *that*
Python object, with the remaining keys passed as constructor arguments. The shipped `configs/pipeline.yaml` looks like
this:

```yaml
_target_: my_project.pipeline.Pipeline   # build a Pipeline(...)
message: hello                           # -> Pipeline(message="hello", ...)
steps:                                   # a list whose items are themselves _target_ objects
  - _target_: my_project.pipeline.Upper
  - _target_: my_project.pipeline.Repeat
    times: 3                             # -> Repeat(times=3)
```

`instantiate` is **recursive**: it builds the inner `Upper()` and `Repeat(times=3)` objects first, assembles them into
the `steps` list, then constructs the outer `Pipeline(steps=[...], message="hello")`. That nested construction — an
object whose arguments are themselves configured objects — is the pattern worth taking away; it's how you assemble a
whole component graph (a model + its optimizer + its data loader, say) purely from config.

`my_project/pipeline.py` just defines plain classes — no Hydra-specific code:

```python
class Upper(Transform):
    def __call__(self, text: str) -> str:
        return text.upper()

@dataclass
class Pipeline:
    steps: list[Transform]
    message: str = "hello"
    def run(self) -> str: ...
```

## OmegaConf and `_convert_`

Hydra parses YAML into an **[OmegaConf](https://omegaconf.readthedocs.io/)** config object (`DictConfig`/`ListConfig`) —
dict-like containers that add interpolation, type checking, and a merge system. Because those aren't plain
`dict`/`list`, the entrypoint passes `_convert_="all"` so `instantiate` hands your classes native Python containers
instead of OmegaConf ones:

```python
@hydra.main(version_base=None, config_path="../my_project/configs", config_name="pipeline")
def main(config: DictConfig) -> None:
    pipeline = instantiate(config, _convert_="all")   # build the graph
    pipeline.run()
```

## Running it and overriding from the CLI

```bash
uv run python scripts/example.py                     # uses configs/pipeline.yaml as-is
uv run python scripts/example.py message="hi there"  # override a top-level value
uv run python scripts/example.py steps.1.times=5     # override a nested list item's param
```

Every value is overridable on the command line with dotted paths (`steps.1.times` = the `times` arg of the second step),
so you reconfigure a run without editing files — which is what makes Hydra valuable for experiments and sweeps.

## When to reach for it

Use Hydra when runs are **parametrized or have swappable components** (experiments, pipelines, training configs). For a
script with one or two flags, plain `argparse`/CLI args are simpler — don't reach for Hydra until the configuration
surface earns it. See the [Hydra docs](https://hydra.cc/docs/patterns/configuring_experiments/) for config groups,
multirun sweeps, and structured configs.
