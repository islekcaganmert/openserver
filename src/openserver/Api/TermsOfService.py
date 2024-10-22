async def main(config) -> str:
    with open(config.Policies.ToS) as f:
        r = f.read()
    return r
