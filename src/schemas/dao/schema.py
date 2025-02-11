from pydantic import BaseModel,Field
from typing import List, Dict, Optional, Union
from datetime import datetime

class UserResponse(BaseModel):
    """
    Pydantic model for user response structure.
    
    Attributes:
        user_id (int): Unique identifier for the user
        name (str): User's name, must be between 2 and 50 characters
    """
    user_id: int
    name: str = Field(..., min_length=2, max_length=50)

class UserRequest(BaseModel):
    """
    Pydantic model for user creation/update requests.
    
    Attributes:
        name (str): User's name, must be between 2 and 50 characters
    """
    name: str = Field(..., min_length=2, max_length=50)

class OrganizationResponse(BaseModel):
    """
    Pydantic model for organization response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    organization_id: int  # Corrected the typo here
    organization: str = Field(..., min_length=2, max_length=50)


class OrganizationRequest(BaseModel):
    """
    Pydantic model for user creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    organization: str = Field(..., min_length=2, max_length=50)

class RoleProfileResponse(BaseModel):
    """
    Pydantic model for role profile response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile_id: int  # Corrected the typo here
    role_profile: str = Field(..., min_length=2, max_length=50)
    level:str = Field(...,max_length=20)
    organization_id: int

class RoleProfileUpdateRequest(BaseModel):
    """
    Request model for updating role profile.
    
    Attributes:
        role_profile (Optional[str]): Name of the role profile
        level (Optional[str]): Level of the role
        organization_id (Optional[int]): ID of the organization
    """
    role_profile: Optional[str] = Field(default=None, min_length=2, max_length=50)
    level: Optional[str] = Field(default=None, max_length=20)
    organization_id: Optional[int] = None

class RoleProfileRequest(BaseModel):
    """
    Pydantic model for role profile creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile: str = Field(..., min_length=2, max_length=50)
    level:str = Field(...,max_length=20)

class RoleProfileCriterionWeightResponse(BaseModel):
    """
    Pydantic model for role profile criterion weight response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile_id: int  
    criterion_weight_json: str

class RoleProfileCriterionWeightRequest(BaseModel):
    """
    Pydantic model for role profile criterion weight creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    criterion_weight_json: str

class SubcriteriaResponse(BaseModel):
    """
    Response model for subcriterion data.
    Attributes:
        subcriterion_id (int): Unique identifier for the subcriterion
        subcriteria (str): Name of the subcriterion, between 2 and 100 characters
        criterion_id (int): ID of the parent category
        question_id (int): ID of the associated question
    """
    subcriterion_id: int
    subcriteria: str = Field(..., min_length=2, max_length=100)
    criterion_id: int
    question_id: int
class SubcriteriaRequest(BaseModel):
    """
    Request model for creating/updating subcriteria.
    Attributes:
        subcriteria (str): Name of the subcriterion, between 2 and 100 characters
        criterion_id (Optional[int]): Optional ID of the parent category
        question_id (int): ID of the associated question
    """
    subcriteria: str = Field(..., min_length=2, max_length=100)
    criterion_id: Optional[int] = None
    question_id: int
class SubcriteriaUpdate(BaseModel):
    """
    Model for updating existing subcriteria.
    Attributes:
        subcriteria (str): New name for the subcriterion, between 2 and 100 characters
    """
    subcriteria: str = Field(..., min_length=2, max_length=100)

class QuestionResponse(BaseModel):
    """
    Pydantic model representing the response structure for a question.
    
    Attributes:
        question_id (int): Unique identifier for the question
        question (str): The actual question text, length between 10-500 characters
        question_type (str): Category or type of the question, length between 3-50 characters
        question_type_id (int): Unique identifier for the question type
    """
    question_id: int
    question: str = Field(..., min_length=10, max_length=500)
    question_type: str = Field(..., min_length=3, max_length=50)
    question_type_id: int

class QuestionRequest(BaseModel):
    """
    Pydantic model for incoming question requests (creation/updates).
    
    Attributes:
        question (Optional[str]): Question text, optional for partial updates
        question_type (Optional[str]): Question category, optional for partial updates
    """
    question: Optional[str] = Field(None, min_length=10, max_length=500)
    question_type: Optional[str] = Field(None, min_length=3, max_length=50)
    
# Pydantic models for request and response validation
class InterviewResponse(BaseModel):
    """
    Response model for interview data.

    Attributes:
        interview_id (int): Unique indentifier for interviews
        user_id (int): ID of the user giving the interview
        interview_date(datetime): Date at which the interview is scheduled
        interview_recording_url(str): Link to the interview recording url
    """
    interview_id: int
    user_id: int
    interview_date: datetime
    interview_recording_url: str

class InterviewRequest(BaseModel):
    """
    Request model for creating or updating Interview data.

    Attributes:
        interview_date(datetime): Date at the which is the interview is scheduled
        interview_recording_url(str): Link to the interview recording url
    """
    interview_date: Optional[datetime] = None
    interview_recording_url: Optional[str] = None

class QuestionEvaluationUpdateRequest(BaseModel):
    """
    Request model for updating question evaluation.

    Attributes:
        score (Optional[float]): Score to be updated
        question_evaluation_json (Optional[str]): Question evaluation json to be updated
    """
    score: Optional[float] = None
    question_evaluation_json: Optional[str] = Field(default=None,min_length=2,max_length=500    )

# Define the schema for adding new evaluations
class QuestionEvaluationRequest(QuestionEvaluationUpdateRequest):
    """
    Request model for adding question evaluation.

    Attributes:
        interview_id (int): ID of the interview
        question_id (int): ID of the question that was asked in interview with provided interview_id
    """
    interview_id: int
    question_id: int

# Define the response schema for question evaluations
class QuestionEvaluationResponse(BaseModel):
    """
    Response model for question evaluation.

    Attributes:
        question_evaluation_id (int): Unique identifier for interview question evaluation table
        interview_id (int): ID of the interview
        question_id (int): ID of the question that was asked in interview with provided interview_id
        score (Optional[float]): Score obtained by the candidate
        question_evaluation_json (Optional[str]): A string that contains question evaluation in a JSON format
    """
    question_evaluation_id: int
    interview_id: int
    question_id: int
    score: Optional[float]
    question_evaluation_json: Optional[str]

# Pydantic model to define the response structure for final evaluation JSON with input validation
class FinalEvaluationResponse(BaseModel):
    """
    Response model for Final Evaluation JSON.

    Attributes:
        final_evaluation_id (int): Unique identifier for the final evaluation
        interview_id (int): Unique identifier for the interview
        final_evaluation_json (str): JSON string containing the evaluation details
    """
    final_evaluation_id : int
    interview_id : int
    final_evaluation_json : str = Field(...,min_length=2,max_length=500)
    final_feedback : str =Field(...,min_length=2,max_length=500)

# Pydantic model to validate incoming final evaluation JSON requests
class FinalEvaluationRequest(BaseModel):
    """
    Request model for updating final evaluation.
    
    Attributes:
        final_evaluation_json (Optional[str]): Final evaluation json to be updated
        final_feedback (Optional[str]): Final feedback to be updated
    """
    final_evaluation_json: Optional[str] = Field(default=None, min_length=2, max_length=500)
    final_feedback: Optional[str] = Field(default=None, min_length=2, max_length=500)

# Pydantic Models for request and response validation
class CriteriaResponse(BaseModel):
    """
    Response model for criteria data.

    Attributes:
        criterion_id (int): Unique indentifier for criteria
         (str): Name of the criteria
        question_type_id (int): ID of the question_type associated with the criteria
    """
    criterion_id: int  # Unique identifier for the criterion
    criterion: str = Field(..., min_length=2)  # Name of the criterion
    question_type_id: int  # ID of the associated question type

class CriteriaRequest(BaseModel):
    """
    Request model for creating or updating criterion.

    Attributes:
         (str):Name of the criteria
    """
    criterion: str = Field(..., min_length=2)  # Name of the criterion

# Pydantic Models Documentation
class ChatHistoryResponse(BaseModel):
    """
    Response model for candidate answer operations with length validation.
    
    Attributes:
        chat_history_turn_id (int): Unique identifier for the chat history entry.
        question_id (int): Reference to the question being answered.
        interview_id (int): Reference to the interview session.
        candidate_answer (str): The answer provided by the candidate, must be between 2 and 500 characters.
    """
    chat_history_turn_id: int
    question_id: int
    interview_id: int
    turn_input: str = Field(..., min_length=2, max_length=500)
    turn_output: str = Field(..., min_length=2, max_length=500)
    turn_input_type: str = Field(..., min_length=2, max_length=20)

class ChatHistoryRequest(BaseModel):
    """
    Request model for candidate answer submissions with length validation.
    
    Attributes:
        candidate_answer (str): The answer provided by the candidate, must be between 2 and 500 characters.
    """
    turn_input: Optional[str] = Field(default=None, min_length=2, max_length=500)
    turn_output: Optional[str] = Field(default=None, min_length=2, max_length=500)
    turn_input_type: Optional[str] = Field(default=None, min_length=2, max_length=20)

