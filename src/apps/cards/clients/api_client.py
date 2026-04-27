from abc import ABC, abstractmethod


class BaseCardApiClient(ABC):
    @abstractmethod
    def get_cards(self, set_id=None) -> list:
        pass

    @abstractmethod
    def get_sets(self) -> list:
        pass

    @abstractmethod
    def get_tags(self) -> list[str]:
        pass

    @abstractmethod
    def get_types(self) -> list[str]:
        pass

    @abstractmethod
    def get_supertypes(self) -> list[str]:
        pass

    @abstractmethod
    def get_rarities(self) -> list[str]:
        pass

    @abstractmethod
    def get_domains(self) -> list[str]:
        pass

    @abstractmethod
    def get_keywords(self) -> list[str]:
        pass
