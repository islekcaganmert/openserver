async def main(config):
    with open(config.Policies.ToS) as f:
        r = f.read()
    return r
