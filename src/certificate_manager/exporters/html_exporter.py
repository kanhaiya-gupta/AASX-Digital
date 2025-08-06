"""
HTML Exporter for Certificate Manager

Generates interactive HTML certificates with expandable sections and styling.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base_exporter import BaseExporter, ExportError


class HTMLExporter(BaseExporter):
    """HTML export implementation with interactive features."""
    
    def __init__(self):
        super().__init__('html')
    
    async def export(self, certificate_id: str, version: str, 
                    template_id: str = 'default', 
                    custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate as interactive HTML."""
        try:
            self.logger.info(f"Starting HTML export for certificate {certificate_id} v{version}")
            
            # Get certificate data
            certificate_data = await self._get_certificate_data(certificate_id, version)
            
            # Generate HTML content
            html_content = self._generate_html_content(certificate_data, template_id, custom_data)
            
            # Add interactive features
            html_content = self._add_interactive_features(html_content, certificate_data)
            
            # Add styling
            html_content = self._add_styling(html_content)
            
            # Compress if needed
            if self._should_compress(html_content):
                html_content = await self._compress_content(html_content)
            
            # Create export data
            export_data = {
                'content': html_content,
                'file_size': len(html_content.encode('utf-8')),
                'mime_type': self.get_mime_type(),
                'file_extension': self.get_file_extension(),
                'filename': self._generate_filename(certificate_id, version)
            }
            
            # Add metadata
            export_data = self._add_export_metadata(export_data, certificate_id, version, template_id)
            
            # Validate export data
            self._validate_export_data(export_data)
            
            self.logger.info(f"HTML export completed for certificate {certificate_id}")
            return export_data
            
        except Exception as e:
            self.logger.error(f"HTML export failed for certificate {certificate_id}: {str(e)}")
            raise ExportError(f"HTML export failed: {str(e)}")
    
    def get_mime_type(self) -> str:
        return 'text/html'
    
    def get_file_extension(self) -> str:
        return 'html'
    
    def _generate_html_content(self, certificate_data: Dict[str, Any], 
                              template_id: str, custom_data: Optional[Dict[str, Any]]) -> str:
        """Generate HTML content from certificate data."""
        certificate = certificate_data['certificate']
        version = certificate_data['version']
        sections = certificate_data['sections']
        
        # Create template data
        template_data = {
            'certificate': certificate,
            'version': version,
            'sections': sections,
            'custom_data': custom_data or {},
            'export_timestamp': datetime.now().isoformat(),
            'template_id': template_id
        }
        
        # Generate HTML structure
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate - {certificate.get('twin_name', 'Unknown')}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="certificate-container">
        <header class="certificate-header">
            <h1>Digital Certificate</h1>
            <div class="certificate-info">
                <p><strong>Certificate ID:</strong> {certificate.get('certificate_id', 'N/A')}</p>
                <p><strong>Twin Name:</strong> {certificate.get('twin_name', 'N/A')}</p>
                <p><strong>Project:</strong> {certificate.get('project_name', 'N/A')}</p>
                <p><strong>Version:</strong> {version.get('version', 'N/A')}</p>
                <p><strong>Created:</strong> {certificate.get('created_at', 'N/A')}</p>
            </div>
        </header>
        
        <main class="certificate-content">
            {self._generate_sections_html(sections)}
        </main>
        
        <footer class="certificate-footer">
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Certificate Hash: {version.get('content_hash', 'N/A')}</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_sections_html(self, sections: Dict[str, Any]) -> str:
        """Generate HTML for certificate sections."""
        if not sections:
            return '<div class="no-sections">No sections available</div>'
        
        sections_html = []
        for section_name, section_data in sections.items():
            section_html = f"""
            <div class="certificate-section" data-section="{section_name}">
                <div class="section-header" onclick="toggleSection('{section_name}')">
                    <h3>{section_name.replace('_', ' ').title()}</h3>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="section-content" id="section-{section_name}">
                    {self._format_section_data(section_data)}
                </div>
            </div>
            """
            sections_html.append(section_html)
        
        return '\n'.join(sections_html)
    
    def _format_section_data(self, section_data: Any) -> str:
        """Format section data for HTML display."""
        if isinstance(section_data, dict):
            return self._format_dict_as_html(section_data)
        elif isinstance(section_data, list):
            return self._format_list_as_html(section_data)
        else:
            return f'<p>{str(section_data)}</p>'
    
    def _format_dict_as_html(self, data: Dict[str, Any]) -> str:
        """Format dictionary as HTML table."""
        if not data:
            return '<p>No data available</p>'
        
        rows = []
        for key, value in data.items():
            formatted_key = key.replace('_', ' ').title()
            formatted_value = self._format_value(value)
            rows.append(f'<tr><td><strong>{formatted_key}</strong></td><td>{formatted_value}</td></tr>')
        
        return f"""
        <table class="section-table">
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _format_list_as_html(self, data: list) -> str:
        """Format list as HTML list."""
        if not data:
            return '<p>No data available</p>'
        
        items = []
        for item in data:
            formatted_item = self._format_value(item)
            items.append(f'<li>{formatted_item}</li>')
        
        return f'<ul class="section-list">{"".join(items)}</ul>'
    
    def _format_value(self, value: Any) -> str:
        """Format a value for HTML display."""
        if isinstance(value, dict):
            return f'<pre>{json.dumps(value, indent=2)}</pre>'
        elif isinstance(value, list):
            return f'<pre>{json.dumps(value, indent=2)}</pre>'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def _add_interactive_features(self, html_content: str, certificate_data: Dict[str, Any]) -> str:
        """Add interactive features to HTML content."""
        # Interactive features are added via JavaScript
        return html_content
    
    def _add_styling(self, html_content: str) -> str:
        """Add CSS styling to HTML content."""
        # Styling is already included in the HTML generation
        return html_content
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the certificate."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .certificate-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .certificate-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .certificate-header h1 {
            margin: 0 0 20px 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .certificate-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .certificate-info p {
            margin: 5px 0;
            font-size: 0.9em;
        }
        
        .certificate-content {
            padding: 30px;
        }
        
        .certificate-section {
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }
        
        .section-header:hover {
            background: #e9ecef;
        }
        
        .section-header h3 {
            margin: 0;
            color: #495057;
            font-size: 1.2em;
        }
        
        .expand-icon {
            font-size: 0.8em;
            transition: transform 0.3s ease;
        }
        
        .section-header.expanded .expand-icon {
            transform: rotate(180deg);
        }
        
        .section-content {
            padding: 0;
            max-height: 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .section-content.expanded {
            padding: 20px;
            max-height: 1000px;
        }
        
        .section-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        
        .section-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .section-table td:first-child {
            width: 30%;
            font-weight: 500;
        }
        
        .section-list {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .section-list li {
            margin: 5px 0;
        }
        
        pre {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.9em;
        }
        
        .certificate-footer {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .no-sections {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 40px;
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features."""
        return """
        function toggleSection(sectionName) {
            const section = document.querySelector(`[data-section="${sectionName}"]`);
            const header = section.querySelector('.section-header');
            const content = section.querySelector('.section-content');
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                header.classList.remove('expanded');
            } else {
                content.classList.add('expanded');
                header.classList.add('expanded');
            }
        }
        
        // Expand all sections
        function expandAllSections() {
            document.querySelectorAll('.section-content').forEach(content => {
                content.classList.add('expanded');
            });
            document.querySelectorAll('.section-header').forEach(header => {
                header.classList.add('expanded');
            });
        }
        
        // Collapse all sections
        function collapseAllSections() {
            document.querySelectorAll('.section-content').forEach(content => {
                content.classList.remove('expanded');
            });
            document.querySelectorAll('.section-header').forEach(header => {
                header.classList.remove('expanded');
            });
        }
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'a') {
                e.preventDefault();
                expandAllSections();
            } else if (e.ctrlKey && e.key === 'c') {
                e.preventDefault();
                collapseAllSections();
            }
        });
        """ 