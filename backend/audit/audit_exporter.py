"""
Real Audit Mode - PDF Export System
Exports decision trails to PDF for auditing purposes
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import base64

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab not available. Install with: pip install reportlab")

@dataclass
class AuditData:
    """Data structure for audit information"""
    decision_id: str
    timestamp: str
    query_data: Dict[str, Any]
    decision: str
    amount: int
    confidence_score: float
    reasoning_tree: Dict[str, Any]
    retrieved_chunks: List[str]
    llm_response: str
    user_id: Optional[str] = None
    override_reason: Optional[str] = None

class AuditExporter:
    """
    Exports decision trails to PDF for auditing
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for the PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='AuditTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='DecisionApproved',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.green,
            backColor=colors.lightgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='DecisionRejected',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            backColor=colors.lightcoral
        ))
    
    def export_decision_audit(self, audit_data: AuditData, output_path: str = None) -> str:
        """
        Export a single decision to PDF audit report
        
        Args:
            audit_data: Audit data for the decision
            output_path: Optional output path
            
        Returns:
            Path to generated PDF
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"audit_report_{audit_data.decision_id}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Add title
        story.append(Paragraph("INSURANCE CLAIM DECISION AUDIT REPORT", self.styles['AuditTitle']))
        story.append(Spacer(1, 20))
        
        # Add basic information
        story.extend(self._create_basic_info_section(audit_data))
        story.append(Spacer(1, 20))
        
        # Add decision details
        story.extend(self._create_decision_section(audit_data))
        story.append(Spacer(1, 20))
        
        # Add reasoning tree
        story.extend(self._create_reasoning_section(audit_data))
        story.append(Spacer(1, 20))
        
        # Add retrieved clauses
        story.extend(self._create_clauses_section(audit_data))
        story.append(Spacer(1, 20))
        
        # Add LLM response
        story.extend(self._create_llm_response_section(audit_data))
        story.append(Spacer(1, 20))
        
        # Add audit trail
        story.extend(self._create_audit_trail_section(audit_data))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Audit report exported to: {output_path}")
        return output_path
    
    def _create_basic_info_section(self, audit_data: AuditData) -> List:
        """Create basic information section"""
        elements = []
        
        elements.append(Paragraph("BASIC INFORMATION", self.styles['SectionHeader']))
        
        # Create table with basic info
        data = [
            ["Decision ID:", audit_data.decision_id],
            ["Timestamp:", audit_data.timestamp],
            ["User ID:", audit_data.user_id or "System"],
            ["Decision Status:", audit_data.decision.upper()],
            ["Coverage Amount:", f"₹{audit_data.amount:,}"],
            ["Confidence Score:", f"{audit_data.confidence_score:.1%}"]
        ]
        
        if audit_data.override_reason:
            data.append(["Override Reason:", audit_data.override_reason])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_decision_section(self, audit_data: AuditData) -> List:
        """Create decision details section"""
        elements = []
        
        elements.append(Paragraph("DECISION DETAILS", self.styles['SectionHeader']))
        
        # Query data table
        query_data = audit_data.query_data
        data = [
            ["Patient Age:", str(query_data.get('age', 'N/A'))],
            ["Gender:", query_data.get('gender', 'N/A')],
            ["Procedure:", query_data.get('procedure', 'N/A')],
            ["Location:", query_data.get('location', 'N/A')],
            ["Policy Duration:", f"{query_data.get('policy_duration_months', 0)} months"]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Decision result
        decision_style = self.styles['DecisionApproved'] if audit_data.decision == 'approved' else self.styles['DecisionRejected']
        elements.append(Paragraph(f"FINAL DECISION: {audit_data.decision.upper()}", decision_style))
        
        return elements
    
    def _create_reasoning_section(self, audit_data: AuditData) -> List:
        """Create reasoning tree section"""
        elements = []
        
        elements.append(Paragraph("REASONING TREE", self.styles['SectionHeader']))
        
        reasoning_tree = audit_data.reasoning_tree
        if 'reasoning_tree' in reasoning_tree:
            steps = reasoning_tree['reasoning_tree']
            
            for i, step in enumerate(steps, 1):
                status_icon = "✅" if step.get('status', False) else "❌"
                step_text = f"{i}. {status_icon} {step.get('step', 'Unknown Step')}"
                elements.append(Paragraph(step_text, self.styles['Normal']))
                
                details = step.get('details', '')
                if details:
                    elements.append(Paragraph(f"   Details: {details}", self.styles['Normal']))
                
                elements.append(Spacer(1, 6))
        
        return elements
    
    def _create_clauses_section(self, audit_data: AuditData) -> List:
        """Create retrieved clauses section"""
        elements = []
        
        elements.append(Paragraph("RETRIEVED POLICY CLAUSES", self.styles['SectionHeader']))
        
        for i, chunk in enumerate(audit_data.retrieved_chunks, 1):
            elements.append(Paragraph(f"Clause {i}:", self.styles['Normal']))
            elements.append(Paragraph(chunk[:500] + "..." if len(chunk) > 500 else chunk, self.styles['Normal']))
            elements.append(Spacer(1, 6))
        
        return elements
    
    def _create_llm_response_section(self, audit_data: AuditData) -> List:
        """Create LLM response section"""
        elements = []
        
        elements.append(Paragraph("LLM RESPONSE", self.styles['SectionHeader']))
        elements.append(Paragraph(audit_data.llm_response, self.styles['Normal']))
        
        return elements
    
    def _create_audit_trail_section(self, audit_data: AuditData) -> List:
        """Create audit trail section"""
        elements = []
        
        elements.append(Paragraph("AUDIT TRAIL", self.styles['SectionHeader']))
        
        trail_data = [
            ["Timestamp", "Action", "Details"],
            [audit_data.timestamp, "Decision Generated", f"System decision: {audit_data.decision}"],
            [audit_data.timestamp, "Confidence Calculated", f"Confidence: {audit_data.confidence_score:.1%}"],
            [audit_data.timestamp, "Clauses Retrieved", f"Retrieved {len(audit_data.retrieved_chunks)} clauses"]
        ]
        
        if audit_data.override_reason:
            trail_data.append([audit_data.timestamp, "Manual Override", audit_data.override_reason])
        
        table = Table(trail_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def export_batch_audit(self, audit_data_list: List[AuditData], output_path: str = None) -> str:
        """
        Export multiple decisions to a single PDF audit report
        
        Args:
            audit_data_list: List of audit data
            output_path: Optional output path
            
        Returns:
            Path to generated PDF
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"batch_audit_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Add title
        story.append(Paragraph("BATCH INSURANCE CLAIM DECISION AUDIT REPORT", self.styles['AuditTitle']))
        story.append(Spacer(1, 20))
        
        # Add summary
        story.extend(self._create_batch_summary(audit_data_list))
        story.append(Spacer(1, 20))
        
        # Add individual decisions
        for i, audit_data in enumerate(audit_data_list, 1):
            story.append(Paragraph(f"DECISION {i}: {audit_data.decision_id}", self.styles['SectionHeader']))
            story.extend(self._create_decision_summary(audit_data))
            story.append(Spacer(1, 15))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Batch audit report exported to: {output_path}")
        return output_path
    
    def _create_batch_summary(self, audit_data_list: List[AuditData]) -> List:
        """Create batch summary section"""
        elements = []
        
        elements.append(Paragraph("BATCH SUMMARY", self.styles['SectionHeader']))
        
        total_decisions = len(audit_data_list)
        approved_count = sum(1 for data in audit_data_list if data.decision == 'approved')
        rejected_count = total_decisions - approved_count
        avg_confidence = sum(data.confidence_score for data in audit_data_list) / total_decisions
        
        summary_data = [
            ["Total Decisions:", str(total_decisions)],
            ["Approved:", str(approved_count)],
            ["Rejected:", str(rejected_count)],
            ["Average Confidence:", f"{avg_confidence:.1%}"],
            ["Date Range:", f"{audit_data_list[0].timestamp} to {audit_data_list[-1].timestamp}"]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_decision_summary(self, audit_data: AuditData) -> List:
        """Create summary for a single decision"""
        elements = []
        
        summary_data = [
            ["Decision:", audit_data.decision.upper()],
            ["Amount:", f"₹{audit_data.amount:,}"],
            ["Confidence:", f"{audit_data.confidence_score:.1%}"],
            ["Procedure:", audit_data.query_data.get('procedure', 'N/A')],
            ["Policy Duration:", f"{audit_data.query_data.get('policy_duration_months', 0)} months"]
        ]
        
        table = Table(summary_data, colWidths=[1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements

class AuditManager:
    """
    Manages audit operations and data collection
    """
    
    def __init__(self):
        self.exporter = AuditExporter()
        self.audit_data_list = []
    
    def add_decision_for_audit(self, decision_data: Dict[str, Any], 
                              user_id: Optional[str] = None) -> str:
        """
        Add a decision for audit tracking
        
        Args:
            decision_data: Decision data from the system
            user_id: Optional user ID
            
        Returns:
            Audit data ID
        """
        audit_data = AuditData(
            decision_id=decision_data.get('decision_id', f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            timestamp=datetime.now().isoformat(),
            query_data=decision_data.get('query_data', {}),
            decision=decision_data.get('decision', 'unknown'),
            amount=decision_data.get('amount', 0),
            confidence_score=decision_data.get('confidence_score', 0.0),
            reasoning_tree=decision_data.get('reasoning_tree', {}),
            retrieved_chunks=decision_data.get('retrieved_chunks', []),
            llm_response=decision_data.get('llm_response', ''),
            user_id=user_id,
            override_reason=decision_data.get('override_reason')
        )
        
        self.audit_data_list.append(audit_data)
        return audit_data.decision_id
    
    def export_single_audit(self, decision_id: str, output_path: str = None) -> str:
        """Export a single decision audit"""
        audit_data = next((data for data in self.audit_data_list if data.decision_id == decision_id), None)
        
        if not audit_data:
            raise ValueError(f"Decision ID {decision_id} not found in audit data")
        
        return self.exporter.export_decision_audit(audit_data, output_path)
    
    def export_batch_audit(self, output_path: str = None) -> str:
        """Export all decisions as batch audit"""
        if not self.audit_data_list:
            raise ValueError("No audit data available for export")
        
        return self.exporter.export_batch_audit(self.audit_data_list, output_path)
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of audit data"""
        if not self.audit_data_list:
            return {"total_decisions": 0}
        
        total_decisions = len(self.audit_data_list)
        approved_count = sum(1 for data in self.audit_data_list if data.decision == 'approved')
        rejected_count = total_decisions - approved_count
        avg_confidence = sum(data.confidence_score for data in self.audit_data_list) / total_decisions
        
        return {
            "total_decisions": total_decisions,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "average_confidence": avg_confidence,
            "date_range": {
                "start": self.audit_data_list[0].timestamp,
                "end": self.audit_data_list[-1].timestamp
            }
        }
