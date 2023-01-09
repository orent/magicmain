exec(compile(
    # The zip from which __main__ was loaded:
    open(__loader__.archive, 'rb').read(
        # minimum offset = size of file before zip start:
        min(f[4] for f in __loader__._files.values())
    ).decode('utf8'),
    __loader__.archive,     # set filename in code object
    'exec'                  # compile in 'exec' mode
))
