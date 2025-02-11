class QuestionNotFoundException(Exception):
    """Exception raised when a question is not found in the database."""
    def __init__(self, question_id):
        self.question_id = question_id
        self.message = f"No question found with question_id: {self.question_id}"
        super().__init__(self.message)

class QuestionTypeNotFoundException(Exception):
    """Exception raised when a question type is not found in the database."""
    def __init__(self, question_type_id):
        self.question_type_id = question_type_id
        self.message = f"No question type found with question_type_id: {self.question_type_id}"
        super().__init__(self.message)

class UserNotFoundException(Exception):
    """Exception raised when a user is not found in the database.""" 
    def __init__(self, user_id):
        self.user_id = user_id
        self.message = f"No user found with user_id: {self.user_id}"
        super().__init__(self.message)

class InterviewNotFoundException(Exception):  
    """Exception raised when a interview is not found in the database."""
    def __init__(self, interview_id):
        self.interview_id = interview_id
        self.message = f"No interview found with interview_id: {self.interview_id}"
        super().__init__(self.message)

class InterviewQuestionNotFoundException(Exception):
    """Exception raised when a question is not found for an interview."""
    def __init__(self,question_id,interview_id):
        self.question_id=question_id
        self.interview_id=interview_id
        self.message=f"No question found with question_id {self.question_id} for the interview with interview_id {self.interview_id}"
        super().__init__(self.message)

class SubcriterionNotFoundException(Exception):
    """Exception raised when a subcriterion is not found."""
    def __init__(self, identifier_name, identifier_value, message="Subcriterion not found for"):
        self.identifier_name = identifier_name
        self.identifier_value = identifier_value
        self.message = f"{message}: {identifier_name}={identifier_value}"
        super().__init__(self.message)

class QuestionEvaluationNotFoundException(Exception):
    """Exception raised when a question evaluation is not found in the database."""
    def __init__(self, question_evaluation_id):
        self.question_evaluation_id = question_evaluation_id
        self.message = f"No question evaluation found with question_evaluation_id: {self.question_evaluation_id}"
        super().__init__(self.message)

class FinalEvaluationNotFoundException(Exception):
    """Exception raised when a final evaluation is not found in the database."""
    def __init__(self, final_evaluation_id):
        self.final_evaluation_id = final_evaluation_id
        self.message = f"No final evaluation found with final_evaluation_id: {self.final_evaluation_id}"
        super().__init__(self.message)

class ChatHistoryNotFoundException(Exception):
    """Exception raised when a chat history is not found in the database."""
    def __init__(self, chat_history_turn_id):
        self.chat_history_turn_id = chat_history_turn_id
        self.message = f"No chat history found with chat_history_turn_id: {self.chat_history_turn_id}"
        super().__init__(self.message)

class CriterionNotFoundException(Exception):
    """Exception raised when a criterion is not found."""
    def __init__(self, identifier_name, identifier_value, message="Criterion not found for"):
        self.identifier_name = identifier_name
        self.identifier_value = identifier_value
        self.message = f"{message}: {identifier_name}={identifier_value}"
        super().__init__(self.message)

class RoleProfileNotFoundException(Exception):
    """Exception raised when a role_profile is not found in the database.""" 
    def __init__(self, role_profile_id):
        self.role_profile_id = role_profile_id
        self.message = f"No role_profile found with role_profile_id: {self.role_profile_id}"
        super().__init__(self.message)

class RoleProfileCriterionWeightNotFoundException(Exception):
    """Exception raised when a role_profile_criterion_weight is not found in the database.""" 
    def __init__(self, role_profile_id):
        self.role_profile_id = role_profile_id
        self.message = f"No role_profile_criterion_weight found with role_profile_id: {self.role_profile_id}"
        super().__init__(self.message)

class OrganizationNotFoundException(Exception):
    """Exception raised when a organization is not found in the database.""" 
    def __init__(self, organization_id):
        self.organization_id = organization_id
        self.message = f"No organization found with organization_id: {self.organization_id}"
        super().__init__(self.message)
