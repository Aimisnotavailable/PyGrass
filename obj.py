import json

class TestOBJ:

    def __init__(self, owner="", content=""):
        self.owner = owner
        self.content = content

    def serialize(self):
        return '{' + f'\"OWNER\" : \"{self.owner}\", \"CONTENT\" : \"{self.content}\"' + '}'

    def deserialize(self, serialized):
        vals = json.loads(serialized)

        self.owner = vals["OWNER"]
        self.content = vals["CONTENT"]

        return self.serialize()