async def main(config):
    r = ''
    with open(config.Policies.ToS, 'r') as f:
        r = f.read()
    return r
