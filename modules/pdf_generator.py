from fpdf import FPDF
import os
from typing import Dict, List, Optional
from datetime import datetime
import re

class AcademicPaperPDF(FPDF):
    """Professional academic paper PDF generator with proper formatting"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up fonts
        font_path = os.path.join(os.path.dirname(__file__), '../fonts/DejaVuSans.ttf')
        bold_font_path = os.path.join(os.path.dirname(__file__), '../fonts/DejaVuSans-Bold.ttf')
        
        self.add_font('DejaVu', '', font_path, uni=True)
        self.add_font('DejaVu', 'B', bold_font_path, uni=True)
        
        # Set default font
        self.set_font('DejaVu', '', 12)
        
        # Set margins for academic paper
        self.set_margins(25, 25, 25)
        self.set_auto_page_break(auto=True, margin=25)
        
        # Initialize page counter
        self.page_count = 0
        
    def _wrap_title(self, title, max_width):
        """Wrap title to fit within max_width on the page."""
        self.set_font('DejaVu', 'B', 18)
        lines = []
        words = title.split()
        current_line = ''
        for word in words:
            test_line = (current_line + ' ' + word).strip()
            if self.get_string_width(test_line) > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines

    def header(self):
        """Professional header with title and page number"""
        if self.page_count > 0:  # Skip header on title page
            self.set_font('DejaVu', '', 10)
            self.set_text_color(100, 100, 100)
            
            # Shorten title for header if needed
            header_title = self.short_title if hasattr(self, 'short_title') else self.title
            if self.get_string_width(header_title) > 120:
                header_title = header_title[:55] + '...'
            self.cell(0, 10, header_title, ln=False, align='L')
            
            # Right header - Page number
            self.cell(0, 10, f'Page {self.page_no()}', ln=True, align='R')
            
            # Header line
            self.line(25, 35, 190, 35)
            self.ln(10)
    
    def footer(self):
        """Professional footer with page number and date"""
        if self.page_count > 0:  # Skip footer on title page
            self.set_y(-15)
            self.set_font('DejaVu', '', 10)
            self.set_text_color(100, 100, 100)
            
            # Footer line
            self.line(25, 280, 190, 280)
            self.ln(5)
            
            # Left footer - Date
            self.cell(0, 10, f'Generated on {datetime.now().strftime("%B %d, %Y")}', ln=False, align='L')
            
            # Right footer - Page number
            self.cell(0, 10, f'Page {self.page_no()}', ln=True, align='R')
    
    def title_page(self, title: str, author: str = "", institution: str = ""):
        """Create professional title page"""
        self.add_page()
        self.page_count += 1
        
        # Center the content vertically
        self.set_y(80)
        
        # Dynamically wrap title
        title_lines = self._wrap_title(title, 150)
        self.set_font('DejaVu', 'B', 18)
        self.set_text_color(40, 40, 120)
        for line in title_lines:
            self.cell(0, 15, line, ln=True, align='C')
        self.ln(10)
        
        # Author
        if author:
            self.set_font('DejaVu', '', 14)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, f"Author: {author}", ln=True, align='C')
            self.ln(5)
        
        # Institution
        if institution:
            self.set_font('DejaVu', '', 12)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, institution, ln=True, align='C')
            self.ln(5)
        
        # Date
        self.set_font('DejaVu', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
        
        # Add some spacing
        self.ln(20)
        
        # Abstract section starts on next page
        self.add_page()
        self.page_count += 1
    
    def section_title(self, title: str, level: int = 1):
        """Format section titles with proper hierarchy"""
        if level == 1:
            # Main section titles
            self.set_font('DejaVu', 'B', 16)
            self.set_text_color(40, 40, 120)
            self.cell(0, 12, title, ln=True)
            self.set_text_color(0, 0, 0)
            self.ln(3)
        elif level == 2:
            # Subsection titles
            self.set_font('DejaVu', 'B', 14)
            self.set_text_color(60, 60, 140)
            self.cell(0, 10, title, ln=True)
            self.set_text_color(0, 0, 0)
            self.ln(2)
        else:
            # Sub-subsection titles
            self.set_font('DejaVu', 'B', 12)
            self.set_text_color(80, 80, 160)
            self.cell(0, 8, title, ln=True)
            self.set_text_color(0, 0, 0)
            self.ln(1)
    
    def _process_text_with_formatting(self, text: str):
        """Process text with proper bold formatting"""
        # Split text by bold markers
        parts = re.split(r'(\*\*.*?\*\*)', text)
        
        current_x = self.get_x()
        start_x = current_x
        
        for part in parts:
            if not part:
                continue
                
            if part.startswith('**') and part.endswith('**'):
                # Bold text
                bold_text = part[2:-2]  # Remove ** markers
                self.set_font('DejaVu', 'B', 12)
                
                # Check if text fits on current line
                text_width = self.get_string_width(bold_text)
                if self.get_x() + text_width > self.w - self.r_margin:
                    self.ln(7)
                    current_x = self.l_margin
                    self.set_x(current_x)
                
                self.cell(text_width, 7, bold_text, ln=False)
                current_x += text_width
                self.set_x(current_x)
                self.set_font('DejaVu', '', 12)  # Back to normal
            else:
                # Regular text
                self.set_font('DejaVu', '', 12)
                
                # Handle line wrapping for long text
                words = part.split(' ')
                for i, word in enumerate(words):
                    if i > 0:
                        word = ' ' + word  # Add space back
                    
                    word_width = self.get_string_width(word)
                    if self.get_x() + word_width > self.w - self.r_margin:
                        self.ln(7)
                        current_x = self.l_margin
                        self.set_x(current_x)
                        word = word.lstrip()  # Remove leading space if we wrapped
                        word_width = self.get_string_width(word)
                    
                    self.cell(word_width, 7, word, ln=False)
                    current_x += word_width
                    self.set_x(current_x)

    def _parse_markdown_text(self, text: str):
        """Parse markdown text and add it to PDF with proper formatting"""
        if not text.strip():
            return
            
        # Split text into paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            lines = paragraph.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Handle headers
                if line.startswith('###'):
                    header_text = line.replace('###', '').strip()
                    self.ln(3)
                    self.set_font('DejaVu', 'B', 12)
                    self.set_text_color(80, 80, 160)
                    self.cell(0, 8, header_text, ln=True)
                    self.set_text_color(0, 0, 0)
                    self.ln(2)
                    continue
                elif line.startswith('##'):
                    header_text = line.replace('##', '').strip()
                    self.ln(4)
                    self.set_font('DejaVu', 'B', 14)
                    self.set_text_color(60, 60, 140)
                    self.cell(0, 10, header_text, ln=True)
                    self.set_text_color(0, 0, 0)
                    self.ln(3)
                    continue
                elif line.startswith('#'):
                    header_text = line.replace('#', '').strip()
                    self.ln(5)
                    self.set_font('DejaVu', 'B', 16)
                    self.set_text_color(40, 40, 120)
                    self.cell(0, 12, header_text, ln=True)
                    self.set_text_color(0, 0, 0)
                    self.ln(3)
                    continue
                
                # Handle bullet points
                if line.startswith('- ') or line.startswith('* '):
                    bullet_text = line[2:].strip()
                    self.set_font('DejaVu', '', 12)
                    self.cell(10, 7, '•', ln=False)
                    
                    # Process bullet text with formatting
                    saved_x = self.get_x()
                    saved_y = self.get_y()
                    
                    # Create a temporary cell to measure height needed
                    remaining_width = self.w - self.l_margin - self.r_margin - 10
                    
                    if '**' in bullet_text:
                        self._process_text_with_formatting(bullet_text)
                        self.ln(7)
                    else:
                        self.multi_cell(remaining_width, 7, bullet_text, align='L')
                    continue
                
                # Handle numbered lists
                if re.match(r'^\d+\.', line):
                    self.set_font('DejaVu', '', 12)
                    if '**' in line:
                        self._process_text_with_formatting(line)
                        self.ln(7)
                    else:
                        self.multi_cell(0, 7, line, align='J')
                    continue
                
                # Regular paragraph with formatting
                if '**' in line:
                    self._process_text_with_formatting(line)
                    self.ln(7)
                else:
                    self.set_font('DejaVu', '', 12)
                    self.multi_cell(0, 7, line, align='J')
                
            # Add space between paragraphs
            self.ln(4)
    
    def _process_inline_formatting(self, text: str):
        """Process inline formatting like **bold** and *italic*"""
        # For now, let's use a simpler approach that works better with FPDF
        # Replace markdown formatting with plain text and use multi_cell
        
        # Remove bold formatting and make the text bold where needed
        if '**' in text:
            # Split by bold markers and alternate formatting
            parts = text.split('**')
            formatted_text = ""
            
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are bold text
                    formatted_text += f"[BOLD]{part}[/BOLD]"
                else:
                    formatted_text += part
            
            # For now, just remove the markers and use regular text
            # TODO: Implement proper mixed formatting
            clean_text = text.replace('**', '')
            self.multi_cell(0, 7, clean_text, align='J')
        else:
            # Regular text
            self.multi_cell(0, 7, text, align='J')
    
    def section_body(self, body: str):
        """Format body text with markdown parsing"""
        if not body.strip():
            return
            
        self.set_font('DejaVu', '', 12)
        self.set_text_color(0, 0, 0)
        
        # Parse markdown and add formatted content
        self._parse_markdown_text(body)
        self.ln(5)
    
    def add_abstract(self, abstract: str):
        """Add abstract section with proper formatting"""
        self.section_title("Abstract", level=1)
        self.section_body(abstract)
    
    def add_keywords(self, keywords: List[str]):
        """Add keywords section with proper formatting"""
        if keywords:
            self.set_font('DejaVu', 'B', 12)
            self.set_text_color(60, 60, 140)
            self.cell(0, 8, "Keywords: ", ln=True)
            self.set_font('DejaVu', '', 12)
            self.set_text_color(0, 0, 0)
            # Join keywords with commas and render as a single line
            keywords_text = ", ".join(keywords)
            self.multi_cell(0, 8, keywords_text, align='L')
            self.ln(5)
    
    def add_references(self, references: List[str]):
        """Add references section with proper formatting"""
        if references:
            self.section_title("References", level=1)
            
            self.set_font('DejaVu', '', 12)
            for i, reference in enumerate(references, 1):
                self.multi_cell(0, 7, f"{i}. {reference}", align='L')
                self.ln(2)
    
    def add_figure(self, image_path: str, caption: str = ""):
        if os.path.exists(image_path):
            self.ln(5)
            self.image(image_path, w=120)
            if caption:
                self.set_font('DejaVu', 'I', 11)
                self.set_text_color(80, 80, 80)
                self.multi_cell(0, 7, f"Figure: {caption}", align='C')
            self.ln(5)

    def add_figures(self, figures: Optional[List[Dict]] = None):
        if figures:
            self.section_title("Figures", level=1)
            for fig in figures:
                self.add_figure(fig.get('image_path', ''), fig.get('caption', ''))

    def add_table_of_contents(self, sections: List[str]):
        """Add table of contents"""
        self.section_title("Table of Contents", level=1)
        
        self.set_font('DejaVu', '', 12)
        for i, section in enumerate(sections, 1):
            self.cell(0, 8, f"{i}. {section}", ln=True)
            self.ln(1)
        
        self.ln(10)


def generate_paper_pdf(paper: Dict[str, str], output_path: str, title: str = "GI Academic Paper", 
                      author: str = "", institution: str = "Geographical Indication Research Team", 
                      keywords: List[str] = None) -> str:
    """
    Generate a professional academic paper PDF
    
    Args:
        paper: Dictionary containing paper sections
        output_path: Path to save the PDF
        title: Paper title
        author: Author name
        institution: Institution name
        keywords: List of keywords
    
    Returns:
        Path to generated PDF
    """
    
    # Initialize PDF
    pdf = AcademicPaperPDF()
    pdf.title = title
    pdf.short_title = title[:50] + "..." if len(title) > 50 else title
    
    # Create title page
    pdf.title_page(title, author, institution)
    
    # Define section order and titles
    section_order = [
        ('abstract', 'Abstract'),
        ('introduction', 'Introduction'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('results', 'Results'),
        ('conclusion', 'Conclusion')
    ]
    
    # Add abstract first
    if 'abstract' in paper and paper['abstract']:
        pdf.add_abstract(paper['abstract'])
        
        # Add keywords after abstract
        if keywords:
            pdf.add_keywords(keywords)
    
    # Add other sections
    for section_key, section_title in section_order[1:]:  # Skip abstract as it's already added
        if section_key in paper and paper[section_key]:
            pdf.section_title(section_title, level=1)
            pdf.section_body(paper[section_key])
    
    # Generate PDF
    pdf.output(output_path)
    
    return output_path


def generate_enhanced_paper_pdf(
    paper: Dict[str, str],
    output_path: str,
    title: str = "GI Academic Paper",
    author: str = "",
    institution: str = "Geographical Indication Research Team",
    keywords: Optional[List[str]] = None,
    references: Optional[List[str]] = None,
    figures: Optional[List[Dict]] = None,
    include_toc: bool = True
) -> str:
    """
    Generate an enhanced academic paper with table of contents and references
    """
    # Initialize PDF
    pdf = AcademicPaperPDF()
    pdf.title = title
    pdf.short_title = title[:50] + "..." if len(title) > 50 else title
    
    # Create title page
    pdf.title_page(title, author, institution)
    
    # Add table of contents if requested
    if include_toc:
        section_titles = ['Abstract', 'Introduction', 'Literature Review', 'Methodology', 'Results', 'Conclusion']
        if figures:
            section_titles.append('Figures')
        if references:
            section_titles.append('References')
        pdf.add_table_of_contents(section_titles)
    
    # Define section order and titles
    section_order = [
        ('abstract', 'Abstract'),
        ('introduction', 'Introduction'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('results', 'Results'),
        ('conclusion', 'Conclusion')
    ]
    
    # Add abstract first
    if 'abstract' in paper and paper['abstract']:
        pdf.section_title('Abstract', level=1)
        pdf.section_body(paper['abstract'])
        
        # Add keywords after abstract
        if keywords:
            pdf.add_keywords(keywords)
    
    # Add other sections
    for section_key, section_title in section_order[1:]:
        if section_key in paper and paper[section_key]:
            pdf.section_title(section_title, level=1)
            pdf.section_body(paper[section_key])
    
    # Add figures if available
    if figures:
        pdf.add_figures(figures)
    
    # Add references if available
    if references:
        pdf.add_references(references)
    
    # Generate PDF
    pdf.output(output_path)
    
    return output_path 