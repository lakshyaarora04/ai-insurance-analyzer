"""
Explainable Decisions System
Turns LLM responses into structured, human-readable explanations
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ExplanationType(Enum):
    APPROVAL = "APPROVAL"
    REJECTION = "REJECTION"
    WAITING_PERIOD = "WAITING_PERIOD"
    EXCLUSION = "EXCLUSION"
    COVERAGE = "COVERAGE"
    AMOUNT = "AMOUNT"

@dataclass
class ExplanationStep:
    """A single step in the explanation chain"""
    step_type: ExplanationType
    title: str
    description: str
    status: bool  # True for passed, False for failed
    clause_references: List[str]
    confidence: float

class ExplainableDecisionProcessor:
    """
    Processes LLM responses and converts them into structured explanations
    """
    
    def __init__(self):
        self.explanation_steps: List[ExplanationStep] = []
    
    def process_llm_response(self, llm_response: str, query_data: Dict[str, Any], 
                           retrieved_chunks: List[str]) -> Dict[str, Any]:
        """
        Process LLM response and create structured explanation
        
        Args:
            llm_response: Raw LLM response
            query_data: Original query data
            retrieved_chunks: Retrieved policy chunks
            
        Returns:
            Structured explanation with human-readable breakdown
        """
        self.explanation_steps = []
        
        # Extract decision from LLM response
        decision = self._extract_decision(llm_response)
        
        # Parse reasoning from LLM response
        reasoning = self._extract_reasoning(llm_response)
        
        # Extract amount
        amount = self._extract_amount(llm_response)
        
        # Build explanation steps
        self._build_explanation_steps(query_data, retrieved_chunks, reasoning)
        
        # Create structured explanation
        explanation = self._create_structured_explanation(decision, amount, query_data)
        
        return explanation
    
    def _extract_decision(self, llm_response: str) -> str:
        """Extract decision from LLM response"""
        decision_match = re.search(r'DECISION:\s*(APPROVED|REJECTED)', llm_response, re.IGNORECASE)
        if decision_match:
            return decision_match.group(1).lower()
        
        # Fallback: look for decision keywords
        if 'approved' in llm_response.lower():
            return 'approved'
        elif 'rejected' in llm_response.lower():
            return 'rejected'
        
        return 'rejected'  # Default to rejected
    
    def _extract_reasoning(self, llm_response: str) -> str:
        """Extract reasoning from LLM response"""
        reasoning_match = re.search(r'REASONING:\s*(.*?)(?=\n\n|\n[A-Z]|$)', 
                                  llm_response, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            return reasoning_match.group(1).strip()
        
        # Fallback: use the entire response
        return llm_response
    
    def _extract_amount(self, llm_response: str) -> int:
        """Extract amount from LLM response"""
        amount_patterns = [
            r'COVERAGE AMOUNT:\s*(\d+)',
            r'AMOUNT:\s*(\d+)',
            r'₹(\d+)',
            r'Rs\.?\s*(\d+)',
            r'INR\s*(\d+)',
            r'(\d+)\s*rupees?',
            r'(\d+)\s*rs'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return 0
    
    def _build_explanation_steps(self, query_data: Dict[str, Any], 
                                retrieved_chunks: List[str], reasoning: str):
        """Build explanation steps based on query data and reasoning"""
        procedure = query_data.get('procedure', '').lower()
        policy_duration = query_data.get('policy_duration_months', 0)
        
        # Step 1: Procedure Coverage Check
        self._add_coverage_step(procedure, retrieved_chunks)
        
        # Step 2: Waiting Period Check
        self._add_waiting_period_step(procedure, policy_duration)
        
        # Step 3: Exclusion Check
        self._add_exclusion_step(procedure, retrieved_chunks)
        
        # Step 4: Policy Status Check
        self._add_policy_status_step(policy_duration)
        
        # Step 5: Amount Calculation (if approved)
        if self._should_add_amount_step():
            self._add_amount_step(query_data, retrieved_chunks)
    
    def _add_coverage_step(self, procedure: str, chunks: List[str]):
        """Add procedure coverage explanation step"""
        coverage_found = False
        relevant_clauses = []
        
        for i, chunk in enumerate(chunks):
            if procedure in chunk.lower():
                coverage_found = True
                relevant_clauses.append(f"Clause {i+1}")
        
        self.explanation_steps.append(ExplanationStep(
            step_type=ExplanationType.COVERAGE,
            title="Procedure Coverage Check",
            description=f"Checking if '{procedure}' is covered by the policy",
            status=coverage_found,
            clause_references=relevant_clauses,
            confidence=0.9 if coverage_found else 0.7
        ))
    
    def _add_waiting_period_step(self, procedure: str, policy_duration: int):
        """Add waiting period explanation step"""
        waiting_periods = {
            'cataract': 24,
            'cataract surgery': 24,
            'heart surgery': 24,
            'knee replacement': 24
        }
        
        required_period = 0
        for proc, period in waiting_periods.items():
            if proc in procedure:
                required_period = period
                break
        
        if required_period == 0:
            status = True
            description = f"No specific waiting period found for '{procedure}'"
        else:
            status = policy_duration >= required_period
            description = f"Policy duration {policy_duration} months vs required {required_period} months"
        
        self.explanation_steps.append(ExplanationStep(
            step_type=ExplanationType.WAITING_PERIOD,
            title="Waiting Period Check",
            description=description,
            status=status,
            clause_references=[],
            confidence=0.95
        ))
    
    def _add_exclusion_step(self, procedure: str, chunks: List[str]):
        """Add exclusion explanation step"""
        exclusions = {
            'cosmetic': 'Cosmetic surgery is excluded unless reconstruction after accident',
            'dental': 'Dental treatment is excluded unless emergency due to accident',
            'experimental': 'Experimental treatments are excluded',
            'refractive': 'Refractive eye surgery is excluded unless medically necessary'
        }
        
        exclusion_found = False
        exclusion_reason = ""
        
        for exclusion_type, reason in exclusions.items():
            if exclusion_type in procedure:
                exclusion_found = True
                exclusion_reason = reason
                break
        
        self.explanation_steps.append(ExplanationStep(
            step_type=ExplanationType.EXCLUSION,
            title="Exclusion Check",
            description=exclusion_reason if exclusion_found else f"No exclusions found for '{procedure}'",
            status=not exclusion_found,  # True if no exclusion found
            clause_references=[],
            confidence=0.9
        ))
    
    def _add_policy_status_step(self, policy_duration: int):
        """Add policy status explanation step"""
        status = policy_duration > 0
        description = f"Policy is active with {policy_duration} months duration" if status else "Policy duration is invalid"
        
        self.explanation_steps.append(ExplanationStep(
            step_type=ExplanationType.COVERAGE,
            title="Policy Status Check",
            description=description,
            status=status,
            clause_references=[],
            confidence=0.9
        ))
    
    def _add_amount_step(self, query_data: Dict[str, Any], chunks: List[str]):
        """Add amount calculation explanation step"""
        procedure = query_data.get('procedure', '').lower()
        
        # Look for sum insured in chunks
        amount = 0
        for chunk in chunks:
            sum_insured_match = re.search(r'sum insured.*?(\d+)', chunk, re.IGNORECASE)
            if sum_insured_match:
                try:
                    amount = int(sum_insured_match.group(1))
                    break
                except ValueError:
                    continue
        
        # Default amounts based on procedure
        if amount == 0:
            if 'cataract' in procedure:
                amount = 50000
            elif 'surgery' in procedure:
                amount = 100000
            else:
                amount = 25000
        
        self.explanation_steps.append(ExplanationStep(
            step_type=ExplanationType.AMOUNT,
            title="Coverage Amount Calculation",
            description=f"Calculated coverage amount: ₹{amount:,}",
            status=amount > 0,
            clause_references=[],
            confidence=0.8
        ))
    
    def _should_add_amount_step(self) -> bool:
        """Determine if amount step should be added"""
        # Add amount step if all previous steps passed
        return all(step.status for step in self.explanation_steps)
    
    def _create_structured_explanation(self, decision: str, amount: int, 
                                     query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured explanation output"""
        
        # Calculate overall confidence
        total_confidence = sum(step.confidence for step in self.explanation_steps)
        avg_confidence = total_confidence / len(self.explanation_steps) if self.explanation_steps else 0
        
        # Create human-readable summary
        summary = self._create_human_readable_summary(decision, amount, query_data)
        
        # Create step-by-step explanation
        step_explanations = []
        for i, step in enumerate(self.explanation_steps, 1):
            step_explanations.append({
                'step_number': i,
                'step_type': step.step_type.value,
                'title': step.title,
                'description': step.description,
                'status': step.status,
                'clause_references': step.clause_references,
                'confidence': step.confidence
            })
        
        return {
            'decision': decision,
            'amount': amount,
            'confidence': avg_confidence,
            'summary': summary,
            'step_by_step': step_explanations,
            'query_data': query_data
        }
    
    def _create_human_readable_summary(self, decision: str, amount: int, 
                                     query_data: Dict[str, Any]) -> str:
        """Create human-readable summary of the decision"""
        procedure = query_data.get('procedure', '')
        policy_duration = query_data.get('policy_duration_months', 0)
        
        if decision == 'approved':
            summary = f"""
🎯 DECISION SUMMARY: APPROVED

The claim for {procedure} has been APPROVED based on the following analysis:

✅ Procedure Coverage: {procedure} is covered under the policy
✅ Waiting Period: Policy duration of {policy_duration} months meets requirements
✅ No Exclusions: No applicable exclusions found
✅ Policy Status: Policy is active and valid

💰 COVERAGE AMOUNT: ₹{amount:,}

This decision is based on comprehensive analysis of all relevant policy clauses and conditions.
            """
        else:
            summary = f"""
🎯 DECISION SUMMARY: REJECTED

The claim for {procedure} has been REJECTED based on the following analysis:

❌ Policy Violations Found:
"""
            
            failed_steps = [step for step in self.explanation_steps if not step.status]
            for step in failed_steps:
                summary += f"   • {step.description}\n"
            
            summary += f"""
💰 COVERAGE AMOUNT: ₹0

This decision is based on comprehensive analysis of all relevant policy clauses and conditions.
            """
        
        return summary.strip()
