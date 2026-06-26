# Hydra

[hydra](https://hydra.cc/) is a framework for code parametrization. This means, that instead of hardcoding, say, the creation of an object in your source code, you replace this with a "pointer" to a config file that allows you to override the parameters to that object creation dynamically. On runtime, you choose which config file and parameter settings you want to use for that object creation. The result is that much of the complexity and verbosity of traditional code is moved from the codebase iself to a set of config files, making your code lean and modular by design. Although particulary useful for configuring experiments, the advantages are general enough to be recommended for general software development.

Configs may reference other configs, and these can be changed dynamically just like the simple parameters in the example above. For more information on common usage patterns with Hydra see [here](https://hydra.cc/docs/patterns/configuring_experiments/)
