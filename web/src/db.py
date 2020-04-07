
db = {
    'data':b'foobar'
}

async def create(id, data):
    db[id] = data.decode("ascii")
    return None

async def get_latest(id):
    return db[id]


async def get_stream(id):
    for i in range(20):
        yield db[id]