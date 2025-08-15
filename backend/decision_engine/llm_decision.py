from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_llm(query_data, clauses):
    """
    Call LLM to evaluate insurance claim based on policy clauses.
    """
    print("🔍 DEBUG: Starting LLM call...")
    
    prompt = f"""
    You are an expert insurance claim evaluator. Your task is to analyze the claim request against the provided policy clauses and make a precise decision.

    CLAIM REQUEST:
    {query_data}

    RELEVANT POLICY CLAUSES:
    {clauses}

    DECISION CRITERIA - APPROVE ONLY IF ALL CONDITIONS ARE MET:

    ✅ APPROVE CONDITIONS (ALL must be true):
    1. WAITING PERIOD MET: Policy duration >= required waiting period for the procedure
    2. NO EXCLUSIONS: Procedure is not explicitly excluded in policy clauses
    3. COVERED PROCEDURE: Procedure is listed as covered or not explicitly excluded
    4. POLICY ACTIVE: Policy is in force and not expired
    5. LOCATION COVERED: Treatment location is within policy coverage area

    ❌ REJECT CONDITIONS (Any one triggers rejection):
    1. WAITING PERIOD NOT MET: Policy duration < required waiting period
    2. EXPLICIT EXCLUSION: Procedure is specifically excluded in policy
    3. UNCOVERED PROCEDURE: Procedure is not mentioned as covered
    4. POLICY EXPIRED: Policy is not active or expired
    5. LOCATION NOT COVERED: Treatment location outside coverage area

    SPECIFIC WAITING PERIOD REQUIREMENTS:
    - Cataract surgery: 24 months (policy_duration >= 24)
    - Specified diseases: 24 months (policy_duration >= 24)
    - Pre-existing conditions: 36 months (policy_duration >= 36)
    - General procedures: 30 days (policy_duration >= 1)

    SPECIFIC EXCLUSIONS TO CHECK:
    - Cosmetic surgery (unless reconstruction after accident/cancer)
    - Dental treatment (unless emergency due to accident)
    - Experimental treatments
    - Treatments outside coverage area
    - Refractive eye surgery (unless medically necessary)

    POLICY EXAMPLES FOR REFERENCE:

    EXAMPLE 1 - APPROVED CLAIM:
    Claim: Cataract surgery, policy_duration=24 months
    Policy Clause: "Cataract surgery covered after 24 months waiting period"
    Decision: APPROVED (waiting period met, procedure covered)
    Reasoning: 24 months policy duration meets 24 months waiting period requirement

    EXAMPLE 2 - REJECTED CLAIM (Waiting Period):
    Claim: Cataract surgery, policy_duration=12 months
    Policy Clause: "Cataract surgery covered after 24 months waiting period"
    Decision: REJECTED (waiting period not met)
    Reasoning: Only 12 months policy duration, requires 24 months

    EXAMPLE 3 - REJECTED CLAIM (Exclusion):
    Claim: Cosmetic surgery, policy_duration=36 months
    Policy Clause: "Cosmetic surgery excluded unless reconstruction after accident"
    Decision: REJECTED (explicit exclusion)
    Reasoning: Cosmetic surgery is explicitly excluded unless for reconstruction

    EXAMPLE 4 - APPROVED CLAIM (Emergency):
    Claim: Emergency heart surgery, policy_duration=6 months
    Policy Clause: "Emergency procedures covered without waiting period"
    Decision: APPROVED (emergency exception)
    Reasoning: Emergency procedures are exempt from waiting periods

    EXAMPLE 5 - REJECTED CLAIM (Uncovered):
    Claim: Dental treatment, policy_duration=24 months
    Policy Clause: "Dental treatment excluded unless emergency due to accident"
    Decision: REJECTED (not emergency)
    Reasoning: Dental treatment is excluded unless emergency due to accident

    DECISION LOGIC:
    1. Extract procedure type from claim request
    2. Check if procedure has waiting period requirement
    3. Compare policy_duration with required waiting period
    4. Search policy clauses for explicit exclusions
    5. Check if procedure is listed as covered
    6. Verify policy is active and location is covered
    7. Make decision based on strict compliance

    CRITICAL: Default to REJECT if any condition is unclear or missing.

    Please provide your response in the following format:
    
    DECISION: [APPROVED/REJECTED]
    
    REASONING: [Detailed explanation with specific clause references. For rejections, clearly explain the specific waiting period, exclusion, or condition that was not met.]
    
    COVERAGE AMOUNT: [Specific amount in rupees if approved, 0 if rejected]
    
    RELEVANT CLAUSES: [List the specific clause numbers that support your decision]
    
    POLICY LIMITS: [Any sum insured or policy limits mentioned in the clauses]
    
    WAITING PERIOD CHECK: [State the waiting period requirement and whether it was met]
    
    EXCLUSION CHECK: [State any exclusions found and whether they apply]
    """

    try:
        # Set OpenAI API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔍 DEBUG: API key found: {'Yes' if api_key else 'No'}")
        if api_key:
            print(f"🔍 DEBUG: API key starts with: {api_key[:10]}...")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize OpenAI client with new API format
        client = OpenAI(api_key=api_key)
        print("🔍 DEBUG: OpenAI client initialized successfully")
        
        print("🔍 DEBUG: Making OpenAI API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,  # Increased for better justifications
            temperature=0.1
        )
        
        print("🔍 DEBUG: OpenAI API call successful")
        result = response.choices[0].message.content
        print(f"🔍 DEBUG: Response length: {len(result)} characters")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in LLM call: {str(e)}")
        print(f"❌ Exception type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return f"Error calling LLM: {str(e)}"
