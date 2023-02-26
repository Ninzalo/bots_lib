import dataclasses
import ast


def dataclass_from_dict(struct, dictionary) -> dict:
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(struct)}
        return struct(
            **{
                f: dataclass_from_dict(fieldtypes[f], dictionary[f])
                for f in dictionary
            }
        )
    except:
        return dictionary


def dataclass_to_dict(cls) -> dict:
    return {k: v for k, v in dataclasses.asdict(cls).items()}


def str_to_dict(string: str) -> dict:
    return ast.literal_eval(string)
