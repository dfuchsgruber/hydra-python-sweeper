
def configure_cli_overrides_python():
    return [
        [('foo', 33), ('+bar', 0)],
        [('foo', 33), ('+bar', 1)],
    ]
    
def configure_2():
    return [
        [('+bizz', 1)],
        [('+bizz', 11)]
    ]
    
def configure_with_subconfig():
    from .subconfigs import subconfig
    from hydra_plugins.python_sweeper_plugin.utils import merge_overrides
    
    return merge_overrides(
        configure_2(),
        subconfig.configure()
    )