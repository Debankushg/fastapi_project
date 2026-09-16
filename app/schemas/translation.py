from pydantic import RootModel


class TranslationsResponse(RootModel[dict[str, str]]):
    pass
