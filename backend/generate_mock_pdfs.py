"""
Generate mock PDF documents for testing the TradePal AI system.

This script creates sample PDFs for:
- Billing/pricing documents
- Technical documentation
- Policy/compliance documents
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


def create_billing_doc(filename):
    """Create a billing/pricing PDF document."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='blue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("TradePal AI Pricing Guide", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Content
    content = [
        ("Subscription Plans", styles['Heading2']),
        ("Our flexible pricing model offers three tiers to meet your needs:", styles['Normal']),
        ("", styles['Normal']),
        
        ("Starter Plan - $29/month", styles['Heading3']),
        ("Perfect for individuals and small teams:", styles['Normal']),
        ("• Up to 5 users", styles['Normal']),
        ("• 1,000 API calls per month", styles['Normal']),
        ("• Email support", styles['Normal']),
        ("• Basic analytics dashboard", styles['Normal']),
        ("• PDF document processing (up to 50 pages/month)", styles['Normal']),
        ("", styles['Normal']),
        
        ("Professional Plan - $99/month", styles['Heading3']),
        ("Ideal for growing businesses:", styles['Normal']),
        ("• Up to 25 users", styles['Normal']),
        ("• 10,000 API calls per month", styles['Normal']),
        ("• Priority email and chat support", styles['Normal']),
        ("• Advanced analytics and reporting", styles['Normal']),
        ("• PDF document processing (up to 500 pages/month)", styles['Normal']),
        ("• Custom agent training", styles['Normal']),
        ("• 99.9% uptime SLA", styles['Normal']),
        ("", styles['Normal']),
        
        ("Enterprise Plan - Custom Pricing", styles['Heading3']),
        ("For large organizations with specific needs:", styles['Normal']),
        ("• Unlimited users", styles['Normal']),
        ("• Unlimited API calls", styles['Normal']),
        ("• 24/7 phone and dedicated support", styles['Normal']),
        ("• White-label options", styles['Normal']),
        ("• Unlimited PDF processing", styles['Normal']),
        ("• Custom integrations and workflows", styles['Normal']),
        ("• On-premise deployment available", styles['Normal']),
        ("• 99.99% uptime SLA", styles['Normal']),
        ("", styles['Normal']),
    ]
    
    for text, style in content:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Billing Information
    story.append(Paragraph("Billing Information", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    billing_content = [
        ("Payment Methods", styles['Heading3']),
        ("We accept all major credit cards (Visa, MasterCard, American Express, Discover), PayPal, and wire transfers for Enterprise customers. All plans are billed monthly in advance.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Invoicing", styles['Heading3']),
        ("Invoices are sent via email on the 1st of each month. Enterprise customers can request custom billing cycles and purchase orders.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Refund Policy", styles['Heading3']),
        ("We offer a 30-day money-back guarantee for new subscriptions. If you're not satisfied within the first 30 days, contact our billing department for a full refund.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Overage Charges", styles['Heading3']),
        ("If you exceed your plan's API call limit, overage charges apply at $0.01 per additional API call. You'll receive email notifications at 80% and 100% of your monthly limit.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Cancellation", styles['Heading3']),
        ("You can cancel your subscription anytime from your account dashboard. Cancellations take effect at the end of your current billing period. No refunds are provided for partial months.", styles['Normal']),
    ]
    
    for text, style in billing_content:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def create_brokerage_doc(filename):
    """Create a concise brokerage and trading guide PDF."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("TradePal Brokerage & Trading Guide", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Trading Fees
    content = [
        ("Trading Fees & Commissions", styles['Heading2']),
        ("Stock Trades: $0 commission per trade", styles['Normal']),
        ("Options Contracts: $0.65 per contract", styles['Normal']),
        ("No account maintenance fees", styles['Normal']),
        ("", styles['Normal']),
        
        ("Day Trading Rules", styles['Heading2']),
        ("Pattern Day Trader (PDT) Rule:", styles['Heading3']),
        ("• Minimum equity requirement: $25,000", styles['Normal']),
        ("• Definition: 4 or more day trades within 5 business days", styles['Normal']),
        ("• Day trade: Opening and closing a position on the same day", styles['Normal']),
        ("• If flagged as PDT with less than $25k: Account restricted to closing positions only for 90 days", styles['Normal']),
        ("• Day trading buying power: Up to 4x your maintenance margin excess", styles['Normal']),
        ("", styles['Normal']),
        
        ("Margin Requirements", styles['Heading2']),
        ("Initial Margin: 50% of stock purchase value", styles['Normal']),
        ("Maintenance Margin: 25% of stock value (must maintain this level)", styles['Normal']),
        ("Margin Call: Occurs when equity falls below maintenance margin requirement", styles['Normal']),
        ("Margin Interest: Typically 8-12% APR, charged on borrowed funds", styles['Normal']),
        ("Minimum for Margin Account: $2,000", styles['Normal']),
        ("", styles['Normal']),
        
        ("Settlement Periods", styles['Heading2']),
        ("Stock Trades: T+2 settlement (trade date + 2 business days)", styles['Normal']),
        ("Options: T+1 settlement", styles['Normal']),
        ("Funds from stock sales available: 2 business days after trade", styles['Normal']),
        ("", styles['Normal']),
        
        ("Options Trading Levels", styles['Heading2']),
        ("Level 1: Covered calls, cash-secured puts", styles['Normal']),
        ("Level 2: Long calls/puts, spreads (requires approval)", styles['Normal']),
        ("Level 3: Naked options writing (requires approval and experience)", styles['Normal']),
        ("Level 4: Complex multi-leg strategies (requires approval)", styles['Normal']),
        ("", styles['Normal']),
        
        ("Account Types", styles['Heading2']),
        ("Cash Account: No margin borrowing, T+2 settlement applies, no pattern day trader restrictions", styles['Normal']),
        ("Margin Account: Allows borrowing, requires $2,000 minimum, subject to PDT rule", styles['Normal']),
        ("IRA Account: Cash only, no margin, no day trading restrictions", styles['Normal']),
        ("", styles['Normal']),
        
        ("Important Trading Rules", styles['Heading2']),
        ("Good Faith Violation (GFV): Buying and selling before funds settle - 3 violations result in 90-day restriction", styles['Normal']),
        ("Free Riding Violation: Buying securities without sufficient funds - immediate 90-day restriction", styles['Normal']),
        ("Wash Sale Rule: Selling at a loss and repurchasing within 30 days - loss disallowed for tax purposes", styles['Normal']),
        ("Short Selling: Requires margin account, must locate shares to borrow, subject to uptick rule", styles['Normal']),
    ]
    
    for text, style in content:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def create_technical_doc(filename):
    """Create a technical documentation PDF."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("TradePal AI Technical Documentation", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # API Documentation
    content = [
        ("API Overview", styles['Heading2']),
        ("The TradePal AI API provides programmatic access to our multi-agent customer service platform. All API requests use JSON and require authentication via API keys.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Authentication", styles['Heading3']),
        ("Include your API key in the Authorization header:", styles['Normal']),
        ("Authorization: Bearer YOUR_API_KEY", styles['Code']),
        ("API keys can be generated from your account dashboard. Keep them secure and never share them publicly.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Chat API Endpoint", styles['Heading3']),
        ("POST /api/chat - Send a message to the AI assistant", styles['Normal']),
        ("", styles['Normal']),
        ("Request Body:", styles['Normal']),
        ('{"message": "What are your pricing plans?", "history": []}', styles['Code']),
        ("", styles['Normal']),
        ("Response:", styles['Normal']),
        ('{"message": "AI response here", "status": "success"}', styles['Code']),
        ("", styles['Normal']),
        
        ("PDF Upload Endpoint", styles['Heading3']),
        ("POST /api/upload - Upload PDF documents for knowledge base", styles['Normal']),
        ("", styles['Normal']),
        ("Form Data:", styles['Normal']),
        ("file: PDF file (required)", styles['Normal']),
        ("document_type: billing|technical|policy (optional)", styles['Normal']),
        ("", styles['Normal']),
    ]
    
    for text, style in content:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Troubleshooting
    story.append(Paragraph("Troubleshooting Guide", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    troubleshooting = [
        ("Common Issues", styles['Heading3']),
        ("", styles['Normal']),
        
        ("Error: 401 Unauthorized", styles['Heading4']),
        ("This error occurs when your API key is invalid or expired. Solution: Generate a new API key from your account dashboard and update your application.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Error: 429 Rate Limit Exceeded", styles['Heading4']),
        ("You've exceeded your plan's API call limit. Solution: Upgrade your plan or wait until your monthly limit resets. Implement exponential backoff in your retry logic.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Error: 500 Server Error", styles['Heading4']),
        ("An internal server error occurred. Solution: Retry your request after a few seconds. If the problem persists, contact support with your request ID.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Slow Response Times", styles['Heading4']),
        ("If you're experiencing slow API responses, check your network connection and ensure you're using the correct regional endpoint. For Enterprise customers, consider using our dedicated infrastructure option.", styles['Normal']),
        ("", styles['Normal']),
        
        ("PDF Processing Failures", styles['Heading4']),
        ("PDFs may fail to process if they're corrupted, password-protected, or contain only images without OCR. Solution: Ensure PDFs are valid, unencrypted, and contain searchable text.", styles['Normal']),
    ]
    
    for text, style in troubleshooting:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def create_policy_doc(filename):
    """Create a policy/compliance PDF document."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkgreen',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("TradePal AI Terms of Service & Privacy Policy", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Terms of Service
    content = [
        ("Terms of Service", styles['Heading2']),
        ("Last Updated: January 1, 2024", styles['Normal']),
        ("", styles['Normal']),
        
        ("1. Acceptance of Terms", styles['Heading3']),
        ("By accessing or using TradePal AI services, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this service.", styles['Normal']),
        ("", styles['Normal']),
        
        ("2. Use License", styles['Heading3']),
        ("Permission is granted to temporarily access TradePal AI services for personal or commercial use only. This is the grant of a license, not a transfer of title, and under this license you may not: modify or copy the materials; use the materials for any commercial purpose without proper licensing; attempt to reverse engineer any software; remove any copyright or proprietary notations.", styles['Normal']),
        ("", styles['Normal']),
        
        ("3. Service Availability", styles['Heading3']),
        ("We strive to maintain 99.9% uptime for Professional plans and 99.99% for Enterprise plans. However, we do not guarantee uninterrupted access and reserve the right to modify or discontinue services with reasonable notice.", styles['Normal']),
        ("", styles['Normal']),
        
        ("4. User Responsibilities", styles['Heading3']),
        ("Users are responsible for maintaining the confidentiality of their API keys and account credentials. You agree not to use the service for any unlawful purpose or in any way that could damage, disable, or impair the service.", styles['Normal']),
        ("", styles['Normal']),
    ]
    
    for text, style in content:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Privacy Policy
    story.append(Paragraph("Privacy Policy", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    privacy = [
        ("Data Collection", styles['Heading3']),
        ("We collect information you provide directly, including name, email, payment information, and API usage data. We also automatically collect technical information such as IP addresses, browser types, and access times.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Data Usage", styles['Heading3']),
        ("Your data is used to provide and improve our services, process payments, send important updates, and comply with legal obligations. We never sell your personal information to third parties.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Data Security", styles['Heading3']),
        ("We implement industry-standard security measures including encryption at rest and in transit, regular security audits, and access controls. All data is stored in SOC 2 Type II certified data centers.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Data Retention", styles['Heading3']),
        ("We retain your data for as long as your account is active or as needed to provide services. After account deletion, personal data is removed within 90 days, except where required by law.", styles['Normal']),
        ("", styles['Normal']),
        
        ("GDPR Compliance", styles['Heading3']),
        ("For European users, we comply with GDPR requirements. You have the right to access, correct, delete, or export your personal data. Contact privacy@tradepal-ai.com to exercise these rights.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Cookies and Tracking", styles['Heading3']),
        ("We use essential cookies for authentication and session management. Optional analytics cookies help us improve the service. You can control cookie preferences in your browser settings.", styles['Normal']),
        ("", styles['Normal']),
        
        ("Contact Information", styles['Heading3']),
        ("For questions about these policies, contact: legal@tradepal-ai.com or mail to TradePal AI Legal Department, 123 Tech Street, San Francisco, CA 94105, USA.", styles['Normal']),
    ]
    
    for text, style in privacy:
        if text:
            story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
    print(f"✓ Created: {filename}")


def main():
    """Generate all mock PDF documents."""
    # Create mock_data directory
    mock_dir = os.path.join(os.path.dirname(__file__), "mock_data")
    os.makedirs(mock_dir, exist_ok=True)
    
    print("Generating mock PDF documents...")
    print()
    
    # Generate documents
    create_billing_doc(os.path.join(mock_dir, "billing_pricing_guide.pdf"))
    create_technical_doc(os.path.join(mock_dir, "technical_documentation.pdf"))
    create_policy_doc(os.path.join(mock_dir, "terms_and_privacy.pdf"))
    create_brokerage_doc(os.path.join(mock_dir, "brokerage_trading_guide.pdf"))
    
    print()
    print(f"✓ All documents created in: {mock_dir}")
    print()
    print("Next steps:")
    print("1. Run: python ingest_mock_data.py")
    print("2. This will process and add all PDFs to ChromaDB")


if __name__ == "__main__":
    # Check for reportlab
    try:
        import reportlab
    except ImportError:
        print("Error: reportlab is required to generate PDFs")
        print("Install it with: pip install reportlab")
        exit(1)
    
    main()


