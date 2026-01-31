from tests.consts import BAR_USE_CASE_RESULT
from tests.deps.core.interfaces import IUseCase


class BarUseCase(IUseCase):
    def execute(self):
        return BAR_USE_CASE_RESULT
