# import statements
import math

def compute_interview_score():
    return None

# def compute_turn_score_interim(turn_assessment_payload = None):
#     if turn_assessment_payload:
#         evaluation_results_list = [] # earlier code sent this as a part of a dictionary from the answer_evaluator.py
#         computed_payload = {}
#         weight_base = 0
#         score_base = 0
#         weight_list = []
#         score_list = []
#         norm_score_subcriterion = 0
#         norm_score_list_subcriterion = []
#         norm_score_criterion = 0
#         norm_score_list_criterion = [] # contains normalised scores at criterion leval; only 7 values for now
#         counter = 0 # counter kept to make the 21 results grouped into 7 for matching evaluation_results ... ugh, need to del this function totally !!!
#         final_score = 0 # simply needs to be the sum of criteria_scores_list; whatever the score, it will be out of 10
        
#         for key in turn_assessment_payload.keys():
#             weight_base = weight_base + turn_assessment_payload[key][0] 
#             score_base = score_base + 10 
        
#         for key in turn_assessment_payload.keys():
#             weight = turn_assessment_payload[key][0]
#             weight = round(weight, 4)
#             score = float(turn_assessment_payload[key][1]) ### need to use float function because the score is a string; why?
#             score = round(score, 4)
#             norm_score_subcriterion = (weight / weight_base) * score 
#             norm_score_subcriterion = round(norm_score_subcriterion, 4)
#             weight_list.append(weight)
#             score_list.append(score)
#             norm_score_list_subcriterion.append(norm_score_subcriterion)
            
#             computed_payload[key] = [weight, score, norm_score_subcriterion]

#             if counter % 3 == 0:
#                 subcrit_dict = {}
#                 subcrit_dict[key] = turn_assessment_payload[key][1]
#                 evaluation_results_list.append(subcrit_dict)
#                 norm_score_criterion = round(norm_score_subcriterion, 4)
#                 counter = counter + 1
#             elif counter % 3 == 1:
#                 norm_score_criterion += round(norm_score_subcriterion, 4)
#                 counter = counter + 1
#             else:
#                 evaluation_results_list[-1][key]=turn_assessment_payload[key][1]
#                 norm_score_criterion += round(norm_score_subcriterion, 4)
#                 norm_score_list_criterion.append(round(norm_score_criterion, 4))
#                 counter = counter + 1

#         final_score = math.fsum(norm_score_list_criterion)
        
#         print("weight_base", weight_base)
#         print("score_base", score_base)
#         print(weight_list)
#         print(score_list)
#         print(norm_score_list_subcriterion)
#         print(norm_score_list_criterion)
#         print("\n")
#         for key, values in computed_payload.items():
#             print (key, values)

#         return {
#             "evaluation_results": evaluation_results_list,
#             "criteria_scores": norm_score_list_criterion,
#             "final_score": final_score
#         }
#     else:
#         print("Turn assessment payload is empty")

def compute_turn_score_interim(turn_assessment_payload=None):
    if not turn_assessment_payload:
        print("Turn assessment payload is empty")
        return

    # Initialize variables
    weight_base = sum(weight for weight, score in turn_assessment_payload.values())
    computed_payload = {}
    norm_score_list_criterion = []
    final_score = 0
    norm_score_subcriteria = []
    
    for i, (subcriterion, (weight, score)) in enumerate(turn_assessment_payload.items()):
        # Normalize subcriterion score
        norm_score = round((weight / weight_base) * score, 4)
        computed_payload[subcriterion] = [round(weight, 4), round(score, 4), norm_score]
        norm_score_subcriteria.append(norm_score)
        
        # Group into criteria and calculate normalized criterion score
        if (i + 1) % 3 == 0:  # Assume 3 subcriteria per criterion
            criterion_score = round(sum(norm_score_subcriteria[-3:]), 4)
            norm_score_list_criterion.append(criterion_score)

    # Final score is the sum of criterion-level scores
    final_score = round(math.fsum(norm_score_list_criterion), 2)

    return norm_score_list_criterion, final_score

# def compute_turn_score_gold_for_later(turn_assessment_payload = None):
#     computed_payload = {}
#     if turn_assessment_payload:
#         weight_base = 0
#         score_base = 0
#         weight_list = []
#         score_list = []
#         norm_score_list = []
#         for key in turn_assessment_payload.keys():
#             weight_base = weight_base + turn_assessment_payload[key][0] 
#             score_base = score_base + float(turn_assessment_payload[key][1]) ### need to use float function because the score is a string; why?
#         for key in turn_assessment_payload.keys():
#             weight = turn_assessment_payload[key][0] 
#             score = float(turn_assessment_payload[key][1])
#             norm_score = (weight / weight_base) * (score / 210) # added a fix score_base of 210(21*10), this could change later
#             #  norm_score = (weight / weight_base) * (score / score_base) 
#             weight_list.append(weight)
#             score_list.append(score)
#             norm_score_list.append(norm_score)
#             computed_payload[key] = [weight, score, norm_score]
#         print("weight_base", weight_base)
#         print("score_base", score_base)
#         print(weight_list)
#         print(score_list)
#         print(norm_score_list)
#         print("\n")
#         for key, values in computed_payload.items():
#             print (key, values)
#     else:
#         print("Turn assessment payload is empty")
