"""
Override + Feedback Mechanism
Allows humans to correct decisions and log feedback for fine-tuning
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class FeedbackType(Enum):
    CORRECTION = "correction"
    IMPROVEMENT = "improvement"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class DecisionStatus(Enum):
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"
    MANUAL_OVERRIDE = "manual_override"
    PENDING_REVIEW = "pending_review"

@dataclass
class FeedbackEntry:
    """A feedback entry for decision correction"""
    id: Optional[str]
    timestamp: str
    original_decision: str
    corrected_decision: str
    feedback_type: str
    user_comment: str
    query_data: Dict[str, Any]
    retrieved_chunks: List[str]
    llm_response: str
    confidence_score: float
    reasoning_tree: Dict[str, Any]
    user_id: Optional[str] = None

class FeedbackDatabase:
    """
    Manages feedback storage and retrieval
    """
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                original_decision TEXT NOT NULL,
                corrected_decision TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                user_comment TEXT,
                query_data TEXT NOT NULL,
                retrieved_chunks TEXT NOT NULL,
                llm_response TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                reasoning_tree TEXT NOT NULL,
                user_id TEXT
            )
        ''')
        
        # Create decision history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL,
                status TEXT NOT NULL,
                query_data TEXT NOT NULL,
                retrieved_chunks TEXT NOT NULL,
                llm_response TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                reasoning_tree TEXT NOT NULL,
                user_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_feedback(self, feedback: FeedbackEntry) -> str:
        """Log a feedback entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate unique ID
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(feedback.timestamp))}"
        feedback.id = feedback_id
        
        cursor.execute('''
            INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback.id,
            feedback.timestamp,
            feedback.original_decision,
            feedback.corrected_decision,
            feedback.feedback_type,
            feedback.user_comment,
            json.dumps(feedback.query_data),
            json.dumps(feedback.retrieved_chunks),
            feedback.llm_response,
            feedback.confidence_score,
            json.dumps(feedback.reasoning_tree),
            feedback.user_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Feedback logged with ID: {feedback_id}")
        return feedback_id
    
    def log_decision(self, decision_data: Dict[str, Any], status: DecisionStatus, 
                    user_id: Optional[str] = None) -> str:
        """Log a decision for history tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate unique ID
        decision_id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(decision_data))}"
        
        cursor.execute('''
            INSERT INTO decision_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            datetime.now().isoformat(),
            decision_data.get('decision', 'unknown'),
            status.value,
            json.dumps(decision_data.get('query_data', {})),
            json.dumps(decision_data.get('retrieved_chunks', [])),
            decision_data.get('llm_response', ''),
            decision_data.get('confidence_score', 0.0),
            json.dumps(decision_data.get('reasoning_tree', {})),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Decision logged with ID: {decision_id}")
        return decision_id
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get feedback statistics
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        cursor.execute('SELECT feedback_type, COUNT(*) FROM feedback GROUP BY feedback_type')
        feedback_by_type = dict(cursor.fetchall())
        
        cursor.execute('SELECT original_decision, corrected_decision, COUNT(*) FROM feedback GROUP BY original_decision, corrected_decision')
        decision_changes = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'feedback_by_type': feedback_by_type,
            'decision_changes': decision_changes
        }
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feedback entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM feedback 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        feedback_entries = []
        for row in rows:
            feedback_entries.append({
                'id': row[0],
                'timestamp': row[1],
                'original_decision': row[2],
                'corrected_decision': row[3],
                'feedback_type': row[4],
                'user_comment': row[5],
                'query_data': json.loads(row[6]),
                'retrieved_chunks': json.loads(row[7]),
                'llm_response': row[8],
                'confidence_score': row[9],
                'reasoning_tree': json.loads(row[10]),
                'user_id': row[11]
            })
        
        return feedback_entries

class FeedbackManager:
    """
    Manages feedback operations and decision overrides
    """
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db = FeedbackDatabase(db_path)
    
    def submit_feedback(self, original_decision: Dict[str, Any], 
                       corrected_decision: str, feedback_type: FeedbackType,
                       user_comment: str, user_id: Optional[str] = None) -> str:
        """
        Submit feedback for a decision
        
        Args:
            original_decision: Original decision data
            corrected_decision: Corrected decision ('approved' or 'rejected')
            feedback_type: Type of feedback
            user_comment: User's comment
            user_id: Optional user ID
            
        Returns:
            Feedback ID
        """
        feedback = FeedbackEntry(
            id=None,
            timestamp=datetime.now().isoformat(),
            original_decision=original_decision.get('decision', 'unknown'),
            corrected_decision=corrected_decision,
            feedback_type=feedback_type.value,
            user_comment=user_comment,
            query_data=original_decision.get('query_data', {}),
            retrieved_chunks=original_decision.get('retrieved_chunks', []),
            llm_response=original_decision.get('llm_response', ''),
            confidence_score=original_decision.get('confidence_score', 0.0),
            reasoning_tree=original_decision.get('reasoning_tree', {}),
            user_id=user_id
        )
        
        return self.db.log_feedback(feedback)
    
    def override_decision(self, original_decision: Dict[str, Any], 
                         new_decision: str, reason: str, 
                         user_id: Optional[str] = None) -> str:
        """
        Override a decision with manual correction
        
        Args:
            original_decision: Original decision data
            new_decision: New decision ('approved' or 'rejected')
            reason: Reason for override
            user_id: Optional user ID
            
        Returns:
            Decision ID
        """
        # Log the override as feedback
        feedback_id = self.submit_feedback(
            original_decision=original_decision,
            corrected_decision=new_decision,
            feedback_type=FeedbackType.CORRECTION,
            user_comment=f"Manual override: {reason}",
            user_id=user_id
        )
        
        # Log the corrected decision
        corrected_decision_data = original_decision.copy()
        corrected_decision_data['decision'] = new_decision
        corrected_decision_data['override_reason'] = reason
        corrected_decision_data['feedback_id'] = feedback_id
        
        decision_id = self.db.log_decision(
            decision_data=corrected_decision_data,
            status=DecisionStatus.MANUAL_OVERRIDE,
            user_id=user_id
        )
        
        print(f"✅ Decision overridden: {original_decision.get('decision')} → {new_decision}")
        return decision_id
    
    def get_feedback_analytics(self) -> Dict[str, Any]:
        """Get analytics about feedback and decision accuracy"""
        summary = self.db.get_feedback_summary()
        
        # Calculate accuracy metrics
        total_feedback = summary['total_feedback']
        corrections = summary['feedback_by_type'].get('correction', 0)
        
        if total_feedback > 0:
            correction_rate = corrections / total_feedback
        else:
            correction_rate = 0
        
        analytics = {
            'total_feedback': total_feedback,
            'correction_rate': correction_rate,
            'feedback_by_type': summary['feedback_by_type'],
            'decision_changes': summary['decision_changes']
        }
        
        return analytics
    
    def export_feedback_data(self, output_file: str = "feedback_export.json"):
        """Export all feedback data for analysis"""
        feedback_entries = self.db.get_recent_feedback(limit=1000)  # Get all feedback
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_entries': len(feedback_entries),
            'feedback_entries': feedback_entries,
            'analytics': self.get_feedback_analytics()
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Feedback data exported to: {output_file}")
        return output_file

class DecisionOverrideUI:
    """
    Simple UI components for decision overrides
    """
    
    @staticmethod
    def create_override_button(decision_id: str, current_decision: str) -> str:
        """Create HTML for override button"""
        opposite_decision = 'approved' if current_decision == 'rejected' else 'rejected'
        
        return f"""
        <div class="override-controls">
            <button onclick="overrideDecision('{decision_id}', '{opposite_decision}')" 
                    class="override-btn">
                Override to {opposite_decision.upper()}
            </button>
            <button onclick="showFeedbackForm('{decision_id}')" 
                    class="feedback-btn">
                Submit Feedback
            </button>
        </div>
        """
    
    @staticmethod
    def create_feedback_form(decision_id: str) -> str:
        """Create HTML for feedback form"""
        return f"""
        <div id="feedback-form-{decision_id}" class="feedback-form" style="display: none;">
            <h3>Submit Feedback</h3>
            <form onsubmit="submitFeedback('{decision_id}', event)">
                <div class="form-group">
                    <label>Feedback Type:</label>
                    <select name="feedback_type" required>
                        <option value="correction">Decision Correction</option>
                        <option value="improvement">System Improvement</option>
                        <option value="bug_report">Bug Report</option>
                        <option value="feature_request">Feature Request</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Comment:</label>
                    <textarea name="comment" rows="4" required 
                              placeholder="Please provide details about your feedback..."></textarea>
                </div>
                <button type="submit" class="submit-btn">Submit Feedback</button>
                <button type="button" onclick="hideFeedbackForm('{decision_id}')" 
                        class="cancel-btn">Cancel</button>
            </form>
        </div>
        """
    
    @staticmethod
    def create_analytics_dashboard() -> str:
        """Create HTML for analytics dashboard"""
        return """
        <div class="analytics-dashboard">
            <h2>Decision Analytics</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>Total Feedback</h3>
                    <span id="total-feedback">0</span>
                </div>
                <div class="metric">
                    <h3>Correction Rate</h3>
                    <span id="correction-rate">0%</span>
                </div>
                <div class="metric">
                    <h3>Manual Overrides</h3>
                    <span id="manual-overrides">0</span>
                </div>
            </div>
            <div class="feedback-summary">
                <h3>Recent Feedback</h3>
                <div id="recent-feedback-list"></div>
            </div>
        </div>
        """
