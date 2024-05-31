class InvalidQuestion(Exception):
    def __str__(self) -> str:
        return "Question is invalid"


class QuestionNeedsСlarification(Exception):
    def __str__(self) -> str:
        return "Question needs clarification"

